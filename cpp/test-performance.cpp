#include <REmatch/REmatch.hpp>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string_view>

std::string get_string_from_file(const std::string &filename) {
  std::ifstream file_stream(filename, std::ios::in | std::ios::binary);
  if (file_stream.is_open()) {
    std::string contents;
    file_stream.seekg(0, std::ifstream::end);
    contents.resize(file_stream.tellg());
    file_stream.seekg(0, std::ifstream::beg);
    file_stream.read(&contents[0], static_cast<long>(contents.size()));
    file_stream.close();
    return contents;
  }
  throw std::runtime_error("Error loading file");
}

int main(int argc, char *argv[]) {
  if (argc < 3) {
    std::cout << "Usage: test-performance <pattern> <document>" << std::endl;
    return EXIT_FAILURE;
  }

  std::string pattern = get_string_from_file(argv[1]);
  std::string document = get_string_from_file(argv[2]);

  REmatch::Query query = REmatch::reql(pattern, REmatch::Flags::NONE, 10, 100000);
  REmatch::MatchGenerator match_generator = query.finditer(document);

  uint64_t count = 0;
  for ([[maybe_unused]] auto &match : match_generator) {
    count++;
  }
  std::cout << count << std::endl;

  return EXIT_SUCCESS;
}
