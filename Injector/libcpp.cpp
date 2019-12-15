#include <stdio.h>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h>

__attribute__ ((visibility ("default"))) void init_debug() {
    spdlog::info("before setup");
    spdlog::flush_every(std::chrono::seconds(3));
    auto file_logger = spdlog::basic_logger_mt("injector", "test.log");

    file_logger->set_level(spdlog::level::info);
    //file_logger->flush_on(spdlog::level::info);

    file_logger->info("file logger created");

    spdlog::set_default_logger(file_logger);  
    spdlog::info("after setup");
}

__attribute__ ((visibility ("default"))) void cel_debug(unsigned long cnt) {
    spdlog::info("cnt jest: {0}", cnt);
}
