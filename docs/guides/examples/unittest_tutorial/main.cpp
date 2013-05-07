#include <iostream>

using namespace std;

class Foo {
	int a_;
public:
	Foo(int a) : a_(a) {
		// Do nothing
	}

	Foo() : a_(0) {
		// Do nothing
	}

	int get_a() const {
		return a_;
	}
};

int bar(int a, int b) {
	cout << "a: " << a << " b: " << b << endl;
	return a + b;
}

int main() {
	return 0;
}
