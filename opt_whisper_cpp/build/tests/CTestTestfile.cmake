# CMake generated Testfile for 
# Source directory: /opt/whisper.cpp/tests
# Build directory: /opt/whisper.cpp/build/tests
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(test-whisper-cli-tiny "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-tiny.bin" "-l" "fr" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-tiny PROPERTIES  LABELS "tiny;gh" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;16;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-tiny.en "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-tiny.en.bin" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-tiny.en PROPERTIES  LABELS "tiny;en" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;23;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-base "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-base.bin" "-l" "fr" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-base PROPERTIES  LABELS "base" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;30;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-base.en "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-base.en.bin" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-base.en PROPERTIES  LABELS "base;en" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;37;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-small "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-small.bin" "-l" "fr" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-small PROPERTIES  LABELS "small" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;44;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-small.en "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-small.en.bin" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-small.en PROPERTIES  LABELS "small;en" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;51;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-medium "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-medium.bin" "-l" "fr" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-medium PROPERTIES  LABELS "medium" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;58;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-medium.en "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-medium.en.bin" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-medium.en PROPERTIES  LABELS "medium;en" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;65;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
add_test(test-whisper-cli-large "/opt/whisper.cpp/build/bin/whisper-cli" "-m" "/opt/whisper.cpp/models/for-tests-ggml-large.bin" "-f" "/opt/whisper.cpp/samples/jfk.wav")
set_tests_properties(test-whisper-cli-large PROPERTIES  LABELS "large" _BACKTRACE_TRIPLES "/opt/whisper.cpp/tests/CMakeLists.txt;72;add_test;/opt/whisper.cpp/tests/CMakeLists.txt;0;")
