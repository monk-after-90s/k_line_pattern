def find_leaf_subclasses(cls):
    """
    查找继承树里的叶子派生类
    """
    # 终末派生类，无派生类
    if not cls.__subclasses__():
        return {cls}
    # 中间派生类
    leaf_subclasses = set()
    for subclass in cls.__subclasses__():
        leaf_subclasses |= find_leaf_subclasses(subclass)
    return leaf_subclasses


if __name__ == '__main__':
    class Parent:
        pass


    class Child1(Parent):
        pass


    class Child2(Parent):
        pass


    class GrandChild(Child1):
        pass


    print(find_leaf_subclasses(Child1))
