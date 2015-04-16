# Dependency Resolver

* Detects circular dependencies in object graph
* Instantiate services with dependencies defined in a dictionary


## Example

```python
from resolver import Resolver

config = {
    'bar': {
        'module': 'example_classes',
        'class': 'Bar',
        'args': ['@foo']
    },
    'foo': {
        'module': 'example_classes',
        'class': 'Foo'
    }
}

resolver = Resolver(config)
services = resolver.do()

foo_service = services['foo'] # Instantiated Foo class
bar_service = services['bar'] # Bar class instantiated with Foo object
```

