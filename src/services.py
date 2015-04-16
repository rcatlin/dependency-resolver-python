""" Services Module """


class InvalidServiceConfiguration(Exception):
    """Raised when a service configuration is Invalid"""


class UninstantiatedServiceException(Exception):
    """
        Raised when a service dependency fullfillment
        is attempted before it has been instantiated.
    """


def is_arg_scalar(arg):
    """ Returns true if arg starts with a dollar sign """
    return arg[:1] == '$'


def is_arg_service(arg):
    """ Returns true if arg starts with an at symbol """
    return arg[:1] == '@'


class ServiceFactory(object):
    """
        Class ServiceFactory handles the dynamic creation of service objects
    """
    def __init__(self, scalars={}):
        self.scalars = scalars
        self.instantiated_services = {}

    # pylint: disable=eval-used, too-many-locals, too-many-arguments
    def create(self, module_name, class_name,
               args=[], kwargs={}, factory_method=None,
               factory_args=[], factory_kwargs={}, static=False,
               calls=None):
        """ Initializes an instance of the service """
        # Verify
        self._verify_args(module_name, class_name, static)

        # Import
        module = self._import_module(module_name)

        # Instantiate
        service_obj = self._instantiate(module, class_name,
                                        args, kwargs, static)
        # Factory?
        if factory_method is not None:
            service_obj = self._handle_factory_method(service_obj,
                                                      factory_method,
                                                      factory_args,
                                                      factory_kwargs)
        # Extra Calls
        if calls is not None and isinstance(calls, list):
            self._handle_calls(service_obj, calls)

        # Return
        return service_obj

    def add_instantiated_service(self, name, service):
        """ Add an instatiated service by name """
        self.instantiated_services[name] = service

    def get_instantiated_services(self):
        """ Get instantiated services """
        return self.instantiated_services

    def get_instantiated_service(self, name):
        if name not in self.instantiated_services:
            raise UninstantiatedServiceException
        return self.instantiated_services[name]

    def _replace_service_arg(self, index, args):
        """ Replace index in list with service """
        args[index] = self.get_instantiated_service(name)

    def _replace_service_kwarg(self, key, kwarg):
        """ Replace key in dictionary with service """
        kwarg[name] = self.get_instantiated_service(key)

    def _replace_scalars_in_args(self, args):
        """ Replaces scalar names in args parameter """
        new_args = []
        for arg in args:
            if isinstance(arg, basestring):
                new_args.append(self._replace_scalar(arg))
            else:
                new_args.append(arg)
        return new_args

    def _replace_scalars_in_kwargs(self, kwargs):
        for (name, value) in kwargs.iteritems():
            if isinstance(value, basestring):
                # Parse Scalars
                kwargs[name] = self._replace_scalar(value)
        return kwargs

    def _replace_services_in_args(self, args):
        new_args = []
        for arg in args:
            if isinstance(arg, basestring):
                new_args.append(self._replace_service(arg))
            else:
                new_args.append(arg)
        return new_args


    def _replace_services_in_kwargs(self, kwargs):
        for (name, value) in kwargs.iteritems():
            if isinstance(value, basestring):
                kwargs[name] = self._replace_service(value)
        return kwargs

    def get_scalar_value(self, name):
        """ Get scalar value by name """
        if name not in self.scalars:
            raise InvalidServiceConfiguration(
                'Invalid Service Argument Scalar "%s" (not found)' % name
            )
        return self.scalars.get(name)

    def _replace_scalar(self, scalar):
        """ Replace scalar name with scalar value """
        if not is_arg_scalar(scalar):
            return scalar
        return self.get_scalar_value(scalar[1:])

    def _replace_service(self, service):
        """ Replace service name with service instance """
        if not is_arg_service(service):
            return service
        return self.get_instantiated_service(service[1:])

    def _verify_args(self, module_name, class_name, static):
        """ Verifies a subset of the arguments to create() """
        # Verify module name is provided
        if module_name is None:
            raise InvalidServiceConfiguration(
                'Service configurations must define a module'
            )

        # Non-static services must define a class
        if not static and class_name is None:
            tmpl0 = 'Non-static service configurations must define a class: '
            tmpl1 = 'module is %s'
            raise InvalidServiceConfiguration((tmpl0 + tmpl1) % module_name)

    def _import_module(self, module_name):
        """ Imports the module dynamically """
        fromlist = []
        dot_position = module_name.rfind('.')
        if dot_position > -1:
            fromlist.append(
                module_name[dot_position+1:len(module_name)]
            )

        # Import module
        module = __import__(module_name, globals(), locals(), fromlist, -1)

        return module

    def _instantiate(self, module, class_name,
                     args=[], kwargs={}, static=False):
        """ Instantiates a class if provided """
        self._check_type('args', args, list)
        self._check_type('kwargs', kwargs, dict)

        if static and class_name is None:
            return module

        if static and class_name is not None:
            return getattr(module, class_name)

        # pylint: disable=unused-variable
        service_obj = getattr(module, class_name)

        # Replace scalars
        new_args = self._replace_scalars_in_args(args)
        new_kwargs = self._replace_scalars_in_kwargs(kwargs)

        # Replace service references
        new_args = self._replace_services_in_args(args)
        new_kwargs = self._replace_services_in_kwargs(kwargs)

        # Instantiate object
        return service_obj(*new_args, **new_kwargs)

    # pylint: disable=unused-argument
    def _handle_factory_method(self, service_obj, method_name,
                               args=[], kwargs={}):
        """" Returns an object returned from a factory method """
        self._check_type('args', args, list)
        self._check_type('kwargs', kwargs, dict)

        # Replace args
        new_args = self._replace_scalars_in_args(args)
        new_kwargs = self._replace_scalars_in_kwargs(kwargs)

        return getattr(service_obj, method_name)(*new_args, **new_kwargs)

    # pylint: disable=unused-argument
    def _handle_calls(self, service_obj, calls):
        """ Performs method calls on service object """
        for call in calls:
            method = call.get('method')
            args = call.get('args')
            kwargs = call.get('kwargs')

            self._check_type('args', args, list)
            self._check_type('kwargs', kwargs, dict)

            if method is None:
                raise InvalidServiceConfiguration(
                    'Service call must define a method.'
                )

            new_args = self._replace_scalars_in_args(args)
            new_kwargs = self._replace_scalars_in_kwargs(kwargs)
            getattr(service_obj, method)(*new_args, **new_kwargs)

    def _check_type(self, name, obj, expected_type):
        """ Raise a TypeError if object is not of expected type """
        if not isinstance(obj, expected_type):
            raise TypeError(
                '"%s" must be an a %s' % (name, expected_type.__name__)
            )
