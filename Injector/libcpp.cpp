#include <stdio.h>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h>

__attribute__ ((visibility ("default"))) void init_debug() {
    auto file_logger = spdlog::basic_logger_st("basic_logger", "test.log");
    spdlog::set_default_logger(file_logger);  

    spdlog::info("one time code");
}

__attribute__ ((visibility ("default"))) void cel_debug(unsigned long cnt) {
    // printf("cnt jest: %li\n", cnt);
    spdlog::info("cnt jest: {0}", cnt);
}
