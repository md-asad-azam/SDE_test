#include <iostream>
#include <string>
#include <algorithm>
#include <cassert>
#include <cctype>

std::string reverse_words(const std::string &str) {
    std::string res = str;
    size_t n = res.size(), start = 0;

    while (start < n) {
        if (std::isalnum(static_cast<unsigned char>(res[start]))) {
            size_t end = start;
            while (end < n && std::isalnum(static_cast<unsigned char>(res[end])))
                ++end;
            std::reverse(res.begin() + start, res.begin() + end);
            start = end;
        } else {
            ++start;
        }
    }
    return res;
}

int main() { 
    std::string test_str = "String; 2be reversed..."; 
    assert(reverse_words(test_str) == "gnirtS; eb2 desrever..."); 

    // more tests
    assert(reverse_words("") == "");
    assert(reverse_words("   ") == "   ");
    assert(reverse_words("Asad") == "dasA");
    assert(reverse_words("He lost his - cool!") == "eH tsol sih - looc!");
    assert(reverse_words("Ph No.- 7488") == "hP oN.- 8847");
    assert(reverse_words("!@#") == "!@#");
    return 0; 
}
