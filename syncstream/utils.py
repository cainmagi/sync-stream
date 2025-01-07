# -*- coding: UTF-8 -*-
"""
Utilities
=========
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
Extensions of the Python STL. Currently this module provides:

1. lazy_import: Lazy import of a Python module. It allows nested imports,
i.e. a lazy-imported module containing other lazy-imported modules.
2. cached_property: Lazy import of a class property. It is the subclass
of the built-in `property`, and thus allows totally the same usage of a
`property`.
"""

import sys
import importlib.abc
import importlib.util
from importlib.util import _LazyModule as _imp_LazyModule  # type: ignore

from types import ModuleType

from typing import Union, Optional, Any, TypeVar

try:
    from typing import Sequence
    from typing import List
except ImportError:
    from collections.abc import Sequence
    from builtins import list as List
from collections.abc import Sequence as _Sequence

from typing_extensions import Literal, Never, TypeGuard, overload

try:  # Suppos that this `utils` module is placed at the root.
    from . import __name__ as __pkg_name__
except ImportError:  # When `utils` is not placed as a submodule.
    __pkg_name__ = None


__all__ = (
    "cancel_type",
    "lazy_import",
    "get_lazy_attribute",
    "is_module_invalid",
    "ModuleReplaceError",
)

K = TypeVar("K")  # Any type.
T = TypeVar("T")  # Any type.


def cancel_type(data: Any) -> Any:
    return data


class ModuleReplaceError(ImportError):
    """Exception raised when replacing an existing lazy module.

    Replacing an existing lazy module is not allowed, because this will cause
    the previously configured lazy module point to a not-existing "real"
    module.
    """


class _LazyModule(_imp_LazyModule):
    """Private class: LazyModule

    Used for providing lazy import.
    """

    __file__: Optional[str] = None
    """The `file` attribute of this placeholder module is empty."""

    removed_kw = set(("__path__",))

    protected_kw = set(
        (
            "__repr__",
            "__str__",
            "__name__",
            "__qualname__",
            "__annotations__",
            "__spec__",
            "__path__",
            "__origin__",
            "__weakref__",
            "__weakrefoffset__",
            "force_load",
            "load_deps",
            "__class__",
            "__dict__",
            "abstract",
        )
    )

    def force_load(self) -> None:
        """Call this method will force the lazy module to be actually loaded.

        This module is used by `load_module` when relative dependency is
        needed to be solved.
        """
        # The following method should be always successful. It will trigger the
        # module loading.
        load_deps = object.__getattribute__(self, "load_deps")
        if callable(load_deps):
            load_deps()
        super().__getattribute__("__name__")

    def load_deps(self) -> None:
        """Search dependencies, and force them to be loaded."""
        self_dict = object.__getattribute__(self, "__dict__")
        if isinstance(self_dict, dict):
            deps = self_dict.get("__dep_modules__", None)
            if deps is not None and isinstance(deps, _Sequence):
                for dep in deps:
                    if isinstance(dep, _LazyModule):
                        dep.force_load()
            self_dict["__dep_modules__"] = tuple()

    def __repr__(self) -> str:
        """This repr is used for showing that this is a lazy module."""
        spec = self.__spec__
        if spec is not None:
            return '<LazyModule {name} from "{path}">'.format(
                name=spec.name, path=spec.origin
            )
        else:
            return super().__repr__()

    def __getattribute__(self, attr: str):
        """Get the attribute of the module.

        If the attribute is missing, load the module.

        Once the module is actually loaded, since the class of the module will
        be replaced by the actual module class, this method will not be used
        any more.
        """
        if attr in _LazyModule.removed_kw:
            raise AttributeError(
                "{0} does not offer the attribute {1}".format(
                    object.__getattribute__(self, "__class__").__name__, attr
                )
            )
        if attr in _LazyModule.protected_kw:
            try:
                return ModuleType.__getattribute__(self, attr)
            except AttributeError:
                pass
        load_deps = object.__getattribute__(self, "load_deps")
        if callable(load_deps):
            load_deps()
        if self.__class__ is not _imp_LazyModule:
            self.__class__ = _imp_LazyModule
        return _imp_LazyModule.__getattribute__(self, attr)


class _LazyAttribute:
    """A lazy attribute of a module.

    This method convert an attribtue from a (lazy or not lazy) module to a "lazy"
    attribute. When it is actually used, the object and its related module will
    be loaded. Otherwise, this attribute will be merely a "placeholder".
    """

    protected_kw = set(
        (
            "__repr__",
            "__str__",
            "__call__",
            "_LazyAttribute__mobj",
            "_LazyAttribute__attr",
            "_LazyAttribute__parent",
            "_LazyAttribute__load_module",
            "_LazyAttribute__obj",
        )
    )

    def __init__(self, mobj: ModuleType, attr: str, parent: str) -> None:
        """Initialization.

        Arguments
        ---------
        mobj: `ModuleType`
            A existing or lazy module object. The attribute will be fetched from it.

        attr: `str`
            The name of the attribute to be fetched. It is a property of `mobj`

        parent: `str`
            The name of the module where this attribute will be assigned to. It will
            be used for locating the parent module and replace the implementation of
            this attribute when this lazy attribute is loaded.
        """
        self.__mobj: ModuleType = mobj
        self.__attr: str = str(attr)
        self.__parent: str = parent
        self.__obj: Any = None

    def __repr__(self) -> str:
        """This repr is used for showing that this is a lazy proxy attribute."""
        return '<LazyAttribute {name} from "{module}">'.format(
            module=object.__getattribute__(self, "_LazyAttribute__mobj").__name__,
            name=self._LazyAttribute__attr,
        )

    def __load_module(self) -> Any:
        """Calling this method will cause the attribute to be loaded."""
        attr_name = object.__getattribute__(self, "_LazyAttribute__attr")
        _obj = object.__getattribute__(self, "_LazyAttribute__obj")
        if _obj is None:
            obj = object.__getattribute__(
                self, "_LazyAttribute__mobj"
            ).__getattribute__(attr_name)
            setattr(
                sys.modules[object.__getattribute__(self, "_LazyAttribute__parent")],
                attr_name,
                obj,
            )
            setattr(self, "_LazyAttribute__obj", obj)
        else:
            obj = _obj
        return obj

    def __call__(self, *args, **kwargs) -> Any:
        """Proxy of __call__ method. After running this method, the attribute will
        be loaded."""
        obj = object.__getattribute__(self, "_LazyAttribute__load_module")()
        if isinstance(obj, type):
            return obj(*args, **kwargs)
        else:
            return obj.__call__(*args, **kwargs)

    def __getattribute__(self, attr: str):
        """Get the attribute of the object.

        If the attribute is missing, load the object.

        Once the object is actually loaded, since the attribute in the parent module
        will be replaced by the actual module class, this method will not be used
        any more.
        """
        if attr in _LazyAttribute.protected_kw:
            try:
                return object.__getattribute__(self, attr)
            except AttributeError:
                pass
        obj = object.__getattribute__(self, "_LazyAttribute__load_module")()
        return getattr(obj, attr)


class _ModulePlaceholder(ModuleType):
    """The placeholder module.
    This module is used as a placeholder of a module that cannot be found.
    It can still provide __name__ property. However, it does not contain
    the __spec__ property.
    """

    __file__: Optional[str] = None
    """The `file` attribute of this placeholder module is empty."""

    removed_kw = set(("__path__",))

    protected_kw = set(
        (
            "__repr__",
            "__str__",
            "__name__",
            "__qualname__",
            "__annotations__",
            "__spec__",
            "__origin__",
            "__weakref__",
            "__weakrefoffset__",
            "force_load",
            "__class__",
            "__dict__",
            "abstract",
        )
    )

    def __init__(self, name: str, doc: Optional[str] = None) -> None:
        """Initialization.

        Arguments
        ---------
        name: `str`
            The module name. It will be passed to ModuleType.

        doc: `str | None`
            The docstring of the placeholder.
        """
        name = str(name)
        if doc is None:
            doc = (
                "{0}\n"
                "This module is used as a placeholder, because the required "
                "module {0} is not found.".format(name)
            )
        else:
            doc = str(doc)
        super().__init__(name=name, doc=doc)
        self.__file__ = None
        self.__path__ = []

    def __repr__(self) -> str:
        """This repr is used for showing that this is a placeholder."""
        return "<ModulePlaceholder {name}>".format(
            name=object.__getattribute__(self, "__name__")
        )

    @property
    def __all__(self) -> Sequence[str]:
        """The attribute list of this placeholder module is empty."""
        return tuple()

    def force_load(self) -> None:
        """Nothing happens. Because this is a placeholder."""
        return

    def __getattribute__(self, attr: str):
        """Add more error information to the attribute error."""
        if attr in _ModulePlaceholder.removed_kw:
            raise AttributeError(
                "{0} does not offer the attribute {1}".format("ModulePlaceholder", attr)
            )
        if attr in _ModulePlaceholder.protected_kw:
            try:
                return object.__getattribute__(self, attr)
            except AttributeError:
                pass
        try:
            return super().__getattribute__(attr)
        except AttributeError as err:
            name = object.__getattribute__(self, "__name__")
            raise ImportError(
                'utils: Fail to fetch the attribute "{0}" from module "{1}" '
                "because this optional module is not successfully loaded. At least "
                "one dependency of this module is not installed.".format(attr, name)
            ) from err


class _LazyLoader(importlib.util.LazyLoader):
    """Private class: LazyLoader

    Used for providing lazy import.
    """

    def __init__(
        self,
        loader: importlib.abc.Loader,
        deps: Sequence[ModuleType],
    ) -> None:
        super().__init__(loader)
        if not isinstance(deps, _Sequence):
            raise TypeError("utils: the dependencies need to be a sequence.")
        for dep in deps:
            if not isinstance(dep, ModuleType):
                raise TypeError("utils: the dependency needs to be a module.")
        self.__dep_modules = tuple(
            filter(lambda dep: isinstance(dep, _LazyModule), deps)
        )

    def exec_module(self, module: ModuleType) -> None:
        """Execute the module.

        This class will configure the properties of the module.
        """
        super().exec_module(module)
        ModuleType.__setattr__(module, "__class__", _LazyModule)
        mdict = object.__getattribute__(module, "__dict__")
        if isinstance(mdict, dict):
            mdict["__dep_modules__"] = self.__dep_modules


class _LazyImporter:
    """The lazy importer.

    This private class is temporarily used during the lazy importing.
    """

    @staticmethod
    def check_is_dep_missing(dependencies: Optional[Union[str, Sequence[str]]]) -> bool:
        """Check if the provided dependencies are missing or not.

        Arguments
        ---------
        dependencies: `str | [str] | None`
            A list of absolute dependencies' names.

        Returns
        -------
        #1: `False` if all dependencies exists.
        """
        if dependencies is None:
            return False
        if isinstance(dependencies, str) or (not isinstance(dependencies, _Sequence)):
            dependencies = (dependencies,)
        for dep in dependencies:
            spec = importlib.util.find_spec(str(dep))
            if spec is None:
                return True
        return False

    @staticmethod
    def gather_relative_module_dependencies(
        rel_dependencies: Optional[Union[ModuleType, Sequence[ModuleType]]],
        is_deps_missing: bool,
    ) -> List[ModuleType]:
        """Gather the dependencies that are relative packages.

        These modules (maynbe lazy) need to be loaded before this module is loaded.

        Arguments
        ---------
        rel_dependencies: `ModuleType | [ModuleType] | None`
            A list of relative dependencies. Each item is a module (can be lazy).
            If using `None`, will return an empty list.

        Returns
        -------
        #1: A list of lazy modules that are the members of the provided relative
            dependencies.
        """
        deps: List[ModuleType] = list()
        if is_deps_missing or rel_dependencies is None:
            return deps
        if isinstance(rel_dependencies, str):
            raise TypeError(
                'utils: The argument "rel_dependencies" should be a module or a '
                "sequence of modules."
            )
        if not isinstance(rel_dependencies, _Sequence):
            rel_dependencies = (rel_dependencies,)
        for dep in rel_dependencies:
            if not isinstance(dep, ModuleType):
                raise ModuleNotFoundError()
        for dep in rel_dependencies:
            if isinstance(dep, _LazyModule):
                deps.append(dep)
        return deps

    @overload
    @staticmethod
    def create_module_placeholder(full_name: str, required: Literal[True]) -> Never: ...

    @overload
    @staticmethod
    def create_module_placeholder(
        full_name: str, required: bool = False
    ) -> _ModulePlaceholder: ...

    @staticmethod
    def create_module_placeholder(full_name: str, required: bool = False):
        """Create a module placeholder.

        Use this method when the lazy-imported module fails to be imported.

        Arguments
        ---------
        full_name: `str`
            The name of the optional module.

        required: `bool`
            If `True`, this method will raise `ModuleNotFoundError`. Otherwise,
            returns a placeholder module.

        Returns
        -------
        #1: `_ModulePlaceholder`
            Return the placeholder only when the `required` is `False`.
        """
        if required:
            raise ModuleNotFoundError(
                "utils: The required module to be lazily loaded is not found: "
                "{0}".format(full_name)
            )
        if sys.modules.get(full_name, None) is not None:
            raise ModuleReplaceError(
                "utils: Try to define a new module placeholder. However, a"
                " previous module has been found. Replacing an existing "
                "(lazy) module or a placeholder with a new placeholder is "
                "not allowed: "
                "{0}".format(full_name)
            )
        module = _ModulePlaceholder(name=full_name)
        sys.modules[full_name] = module
        return module

    @classmethod
    def lazy_import(
        cls,
        name: str,
        package: Optional[str] = __pkg_name__,
        required: bool = True,
        dependencies: Optional[Union[str, Sequence[str]]] = None,
        rel_dependencies: Optional[Union[ModuleType, Sequence[ModuleType]]] = None,
    ) -> ModuleType:
        """Perform the lazy import for a module.
        The returned module will not be loaded until it is actually used.

        Modified from:
        https://docs.python.org/3/library/importlib.html#implementing-lazy-imports

        Arguments
        ---------
        see the module method `lazy_import()`.

        Returns
        -------
        #1: `ModuleType`
            A lazy loaded module. It will be loaded when actually using it.
        """
        full_name = ".".join(map(str, filter(bool, (package, name))))
        # Fetch the module directly if it has been loaded.
        prev_module = sys.modules.get(full_name, None)
        if isinstance(prev_module, ModuleType):
            return prev_module
        # Fail to hit the module.
        # Start the check all absolute module dependencies.
        is_deps_missing = cls.check_is_dep_missing(dependencies)
        # Gather the relative module dependencies, send them to the module loader.
        deps = cls.gather_relative_module_dependencies(
            rel_dependencies, is_deps_missing=is_deps_missing
        )
        # Start to create the lazy-loaded module.
        if package is None:
            spec = importlib.util.find_spec(name)
        else:
            spec = importlib.util.find_spec(".{0}".format(name), package=package)
        if is_deps_missing or (spec is None):
            return cls.create_module_placeholder(full_name=full_name, required=required)
        if spec.loader is None:
            raise TypeError(
                "utils: The spec.loader of the required module is None, which cannot"
                "be used for establishing the lazily loaded module: {0}".format(spec)
            )
        loader = _LazyLoader(spec.loader, deps)
        spec.loader = loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[full_name] = module
        loader.exec_module(module)
        return module


def lazy_import(
    name: str,
    package: Optional[str] = __pkg_name__,
    required: bool = True,
    dependencies: Optional[Union[str, Sequence[str]]] = None,
    rel_dependencies: Optional[Union[ModuleType, Sequence[ModuleType]]] = None,
) -> ModuleType:
    """Perform the lazy import for a module.
    The returned module will not be loaded until it is actually used.

    Modified from:
    https://docs.python.org/3/library/importlib.html#implementing-lazy-imports

    Arguments
    ---------
    name: `str`
        The name of the module. It does not need to start with the `.` symbol.

    package: `str | None`
        The name of the package (anchor).

        By default: will use the `__name__` of the pacakge where this
            `utils` module is placed. if `utils` is not placed as a sub-
            module, and `package` is not specified, will search `name` by
            absolute import.

        If using `None`: will search `name` by absolute import.

    required: `bool`
        Whether to require the existence of the module. If not specified,
        will allow to load an empty module when the module is not found.

    dependencies: `str | [str] | None`
        One or more depdencies for the module to be loaded.

        If not specified, it means that the module does not need
        dependencies. If specified, the module is only loaded when
        all dependencies are detected. Otherwise, returns a module
        placeholder. The dependencies are module names following the
        abosolute import rules.

    rel_dependencies: `ModuleType | [ModuleType] | None`
        One or more relative dependencies. Each item is a module (can be lazy).
        If using `None`, will return an empty list.

    Returns
    -------
    #1: `ModuleType`
        A lazy loaded module. It will be loaded when actually using it.
    """
    return _LazyImporter().lazy_import(
        name=name,
        package=package,
        required=required,
        dependencies=dependencies,
        rel_dependencies=rel_dependencies,
    )


def get_lazy_attribute(
    module: ModuleType, attr: str, parent: str
) -> Optional[_LazyAttribute]:
    """Get an attribute of a lazy module. This attribute will not be loaded if it
    is not accessed.

    If the provided module is invalid, will return `None`.
    """
    if is_module_invalid(module):
        return None
    return _LazyAttribute(module, attr, parent)


def is_module_invalid(module: ModuleType) -> TypeGuard[_ModulePlaceholder]:
    """Check whether a lazy module is invalid.

    Arguments
    ---------
    module: `ModuleType`
        Can be a lazy module, a module or a module placeholder.

    Returns
    -------
    #1: `bool`
        `True` only when the given module is a module placeholder.
    """
    return isinstance(module, _ModulePlaceholder)
