#include <iostream>
#include <algorithm>
#include <spdlog/spdlog.h>
#include "BPatch.h"
#include "BPatch_function.h"
#include "BPatch_point.h"
#include "BPatch_object.h"

/* Workflow:
    - create library (*.so) with functions that you want to debug
        - copy functions declarations and add _debug at the end e.g.
            original function: void some_function(int a, int* b)
            create: void some_function_debug(int a, int* b)
        - build library: gcc -shared -fPIC -o name.so source.c
    - run injector:
        ./injector binary your_lib.so
        this will create binary_debug file
        copy your_lib.so so it can be found by linker (e.g. /usr/lib)
        or set LD_LIBARY_PATH=/path/to/your/lib
    - run your changed binary
*/

using functionsVector = std::vector<BPatch_function*>;
using pointsVector = std::vector<BPatch_point*>;
using paramsVector = std::vector<BPatch_localVar*>;

class originalFunction {
    functionsVector funcs;
    pointsVector *points = nullptr;
    std::size_t paramsNum = 0;

    public:
        originalFunction(BPatch_image* binImage, std::string function) {
            binImage->findFunction(function.c_str(), funcs);
            if(funcs.size() != 0) {
                points = funcs[0]->findPoint(BPatch_entry);
                auto params = funcs[0]->getParams();
                paramsNum = params->size();
            }
        }

        pointsVector* getPoints() { return this->points; }
        auto getParamsNum() { return this->paramsNum; }
};

class Snippet {
    std::vector<BPatch_paramExpr> params;
    std::vector<BPatch_snippet*> args;
    originalFunction* orgFunc = nullptr;
    BPatch_function* libFunc = nullptr;
    BPatch_snippet func;

    public:
        Snippet(BPatch_function* libFunc, originalFunction* orgFunc):
            orgFunc(orgFunc), libFunc(libFunc) {}

        BPatch_snippet* createSnippet() {
            if(orgFunc != nullptr) {
                for(int a=0; a<orgFunc->getParamsNum(); a++) {
                    params.push_back(BPatch_paramExpr(a));
                    args.push_back(&params[a]);
                }
            }

            BPatch_funcCallExpr funcCall(*libFunc, args);
            func = funcCall;
            return &func;
        }
};

class Injector {
    std::string libraryFile = "";
    std::string binaryFile = "";

    BPatch bpatch;
    BPatch_addressSpace* app = nullptr;
    BPatch_image* image = nullptr;
    BPatch_object* lib = nullptr;
    std::vector<BPatch_function*>* libFuncs = nullptr;

    const std::string sufix = "_debug";
    const size_t sufixLen = 6;

    public:
        Injector(std::string binary, std::string library):
            binaryFile(binary), libraryFile(library) {}

        bool loadLibrary() {
            this->lib = this->app->loadLibrary(this->libraryFile.c_str());
            return this->lib != nullptr;
        }

        bool getLibraryFunctions() {
            std::vector<BPatch_module*> modules;
            this->lib->modules(modules);
            if(modules.size() != 1) { return false; }
            this->libFuncs = modules[0]->getProcedures();
            return true;
        }

        int filterLibraryFunctions() {
            // Leave only functions which names end with sufix
            this->libFuncs->erase(
                    std::remove_if(this->libFuncs->begin(), this->libFuncs->end(),
                    [this](auto el){ return std::string(el->getName()).find(this->sufix) == std::string::npos; }),
                this->libFuncs->end());
            return this->libFuncs->size();
        }

        bool openBinary() {
            this->app = this->bpatch.openBinary(this->binaryFile.c_str());
            return this->app != nullptr;
        }

        bool getImage() {
            this->image = this->app->getImage();
            return this->image != nullptr;
        }

        std::string getOriginalFuntionName(std::string debugName) {
            return debugName.substr(0, debugName.size() - this->sufixLen);
        }

        void InsertSnippets() {
            for(auto func: *(this->libFuncs)) {
                auto realName = this->getOriginalFuntionName(func->getName());

                auto realFunc = originalFunction(this->image, realName);

                auto snippetObj = Snippet(func, &realFunc);
                auto snippet = snippetObj.createSnippet();

                if(!this->app->insertSnippet(*snippet, *(realFunc.getPoints()))) {
                    spdlog::error("Could not add snippet: {0}", func->getName());
                }

                spdlog::info("Created snippet for: {0}", func->getName());
            }
        }

        std::string newOutputName() {
            return this->binaryFile + "_debug";
        }

        void writeBinary() {
            auto bin = static_cast<BPatch_binaryEdit*>(this->app);
            auto newName = this->newOutputName();
            bin->writeFile(newName.c_str());
            spdlog::info("File {0} created", newName);
        }

        void main() {
            spdlog::info("Opening binary...");
            if(!this->openBinary()) {
                spdlog::error("Could not open binary: {0}", this->libraryFile);
                return;
            }

            spdlog::info("Getting image...");
            if(!this->getImage()) {
                spdlog::error("Could not get image");
                return;
            }

            spdlog::info("Loading library...");
            if(!this->loadLibrary()) {
                spdlog::error("Could not open library: {0}", this->libraryFile);
                return;
            }

            spdlog::info("Getting lib functions...");
            if(!this->getLibraryFunctions()) {
                spdlog::error("Invalid number of modules in the library");
                return;
            }

            spdlog::info("Filtering lib functions...");
            if(this->filterLibraryFunctions() == 0) {
                spdlog::error("No valid functions found in the library");
                return;
            }

            spdlog::info("Inserting snippets...");
            this->InsertSnippets();

            spdlog::info("Writing new binary...");
            this->writeBinary();
        }
};

int main(int argc, char* argv[]) {
    if(argc != 3) {
        std::cout << argv[0] << " <binary> <library.so>" << std::endl;
        return 0;
    }

    spdlog::info("Starting instrumentation...");

    Injector inj(argv[1], argv[2]);
    inj.main();

    spdlog::info("Done");
}