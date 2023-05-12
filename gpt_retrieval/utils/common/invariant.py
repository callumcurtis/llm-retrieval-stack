from typing import Callable, Any, TypeVar, Type


C = TypeVar('C')


def invariant_method(assertions: Callable[[C], None]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(method: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(self: C, *args: Any, **kwargs: Any) -> Any:
            assertions(self)
            result = method(self, *args, **kwargs)
            assertions(self)
            return result
        return wrapper
    return decorator


def invariant(assertions: Callable[[C], None]) -> Callable[[Type[C]], Type[C]]:
    invariant_method_decorator = invariant_method(assertions)
    def decorator(cls: Type[C]) -> Type[C]:
        for attr in cls.__dict__:
            if not attr.startswith('_') and callable(getattr(cls, attr)):
                method = getattr(cls, attr)
                setattr(cls, attr, invariant_method_decorator(method))
        return cls
    return decorator
