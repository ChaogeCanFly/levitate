"""Implementation of algorithm wrapper protocol."""

import numpy as np


class AlgorithmImplementationMeta(type):
    """Metaclass to wrap `AlgorithmImplementation` objects in `Algorithm` objects.

    API-wise it is nice to call the implementation classes when requesting an algorithm.
    Since the behavior of the objects should change depending on if they are added etc,
    it would be very difficult to keep track of both the current state and the actual algorithm
    in the same top level object. This class will upon object creation instantiate the called class,
    but also instantiate and return an `Algorithm`-type object.
    """

    def __call__(cls, *cls_args, weight=None, position=None, **cls_kwargs):
        """Instantiate an `Algorithm`-type object, using the `cls` as the base algorithm implementation.

        The actual `Algorithm`-type will be chosen based on which optional parameters are passed.
        If no parameters are passed (default) an `Algorithm` object is returned.
        If `weight` is passed an `UnboundCostFunction` object is returned.
        If `position` is passed a `BoundAlgorithm` object is returned.
        If both `weight` and `position` is passed a `CostFunction` object is returned.

        Parameters
        ----------
        cls : class
            The `AlgorithmImplementation` class to use for calculations.
        *cls_args :
            Args passed to the `cls`.
        weight : numeric
            Optional weight.
        position : numpy.ndarray
            Optional array to bind the algorithm to, shape (3,...).
        **cls_kwargs :
            Keyword arguments passed to `cls`.

        """
        obj = cls.__new__(cls, *cls_args, **cls_kwargs)
        obj.__init__(*cls_args, **cls_kwargs)
        if weight is None and position is None:
            alg = Algorithm(algorithm=obj)
        elif weight is None:
            alg = BoundAlgorithm(algorithm=obj, position=position)
        elif position is None:
            alg = UnboundCostFunction(algorithm=obj, weight=weight)
        elif weight is not None and position is not None:
            alg = CostFunction(algorithm=obj, weight=weight, position=position)
        return alg


class AlgorithmImplementation(metaclass=AlgorithmImplementationMeta):
    """Base class for AlgorithmImplementations.

    The attributes listed below are part of the API and should be
    implemented in subclasses.

    Parameters
    ----------
    array : TransducerArray
        The array object to use for calculations.

    Attributes
    ----------
    values_require : dict
        Each key in this dictionary specifies a requirement for
        the `values` method. The wrapper classes will manage
        calling the method with the specified arguments.
    jacobians_require : dict
        Each key in this dictionary specifies a requirement for
        the `jacobians` method. The wrapper classes will manage
        calling the method with the specified arguments.

    Methods
    -------
    values
        Method to calculate the value(s) for the algorithm.
    jacobians
        Method to calculate the jacobians for the algorithm.
        This method is optional if the implementation is not used
        as a cost function in optimizations.

    """

    def __init__(self, array, *args, **kwargs):
        self.array = array

    def __eq__(self, other):
        return type(self) == type(other) and self.array == other.array


def requirement(**requirements):
    """Parse a set of requirements.

    `AlgorithmImplementation` objects should define requirements for values and jacobians.
    This function parses the requirements and checks that the request can be met upon call.
    Currently the inputs are converted to a dict and returned as is, but this might change
    without warning in the future.

    Keyword arguments
    ---------------------
    complex_transducer_amplitudes
        The algorithm requires the actual complex transducer amplitudes directly.
        This is a fallback requirement when it is not possible to implement and algorithm
        with the other requirements, and no performance optimization is possible.
    pressure_derivs_summed
        The number of orders of Cartesian spatial derivatives of the total sound pressure field.
        Currently implemented to third order derivatives.
        See `levitate.utils.pressure_derivs_order` and `levitate.utils.num_pressure_derivs`
        for a description of the structure.
    pressure_derivs_summed
        Like pressure_derivs_summed, but for individual transducers.
    spherical_harmonics_summed
        A spherical harmonics decomposition of the total sound pressure field, up to and
        including the order specified.
        where remaining dimensions are determined by the positions.
    spherical_harmonics_individual
        Like spherical_harmonics_summed, but for individual transducers.

    Returns
    -------
    requirements : dict
        The parsed requirements.

    Raises
    ------
    NotImplementedError
        If one or more of the requested keys is not implemented.

    """
    possible_requirements = [
        'complex_transducer_amplitudes',
        'pressure_derivs_summed', 'pressure_derivs_individual',
        'spherical_harmonics_summed', 'spherical_harmonics_individual',
    ]
    for requirement in requirements:
        if requirement not in possible_requirements:
            raise NotImplementedError("Requirement '{}' is not implemented for an algorithm. The possible requests are: {}".format(requirement, possible_requirements))
    return requirements


class AlgorithmMeta(type):
    """Metaclass for `Algorithm`-type objects.

    This metaclass is only needed to make the `_type` property available
    at both class and instance level.
    """

    @property
    def _type(cls):
        """The type of the algorithm.

        In this context `type` refers for the combination of `bound` and `cost`.
        """
        return cls._is_bound, cls._is_cost


class AlgorithmBase(metaclass=AlgorithmMeta):
    """Base class for all algorithm type objects.

    This wraps a few common procedures for algorithms,
    primarily dealing with preparation and evaluation of requirements
    for algorithm implementations.
    The algorithms support some numeric manipulations to simplify
    the creation of variants of the basic types.
    Not all types of algorithm support all operations, and the order of
    operation can matter in some cases.
    If unsure if the arithmetics return the desired outcome, print the
    resulting object to inspect the new structure.

    Note
    ----
    This class should not be instantiated directly.
    """

    @property
    def _type(self):
        """The type of the algorithm.

        In this context `type` refers for the combination of `bound` and `cost`.
        """
        return type(self)._type

    def __eq__(self, other):
        return type(self) == type(other)

    def _evaluate_requirements(self, complex_transducer_amplitudes, spatial_structures):
        """Evaluate requirements for given complex transducer amplitudes.

        Parameters
        ----------
        complex_transducer_amplitudes: complex ndarray
            The transducer phase and amplitude on complex form,
            must correspond to the same array used to create the algorithm.
        spatial_structures: dict
            Dictionary with the calculated spatial structures required by the algorithm(s).

        Returns
        -------
        requirements : dict
            Has (at least) the same fields as `self.requires`, but instead of values specifying the level
            of the requirement, this dict has the evaluated requirement at the positions and
            transducer amplitudes specified.

        """
        requirements = {}
        if 'complex_transducer_amplitudes' in self.requires:
            requirements['complex_transducer_amplitudes'] = complex_transducer_amplitudes
        if 'pressure_derivs' in spatial_structures:
            requirements['pressure_derivs_individual'] = np.einsum('i,ji...->ji...', complex_transducer_amplitudes, spatial_structures['pressure_derivs'])
            requirements['pressure_derivs_summed'] = np.sum(requirements['pressure_derivs_individual'], axis=1)
        if 'spherical_harmonics' in spatial_structures:
            requirements['spherical_harmonics_individual'] = np.einsum('i,ji...->ji...', complex_transducer_amplitudes, spatial_structures['spherical_harmonics'])
            requirements['spherical_harmonics_summed'] = np.sum(requirements['spherical_harmonics_individual'], axis=1)
        return requirements

    def _spatial_structures(self, position=None):
        """Calculate spatial structures.

        Uses `self.requires` to fill a dictionary of calculated required
        spatial structures at a give position to satisfy the algorithm(s) used
        for calculations.

        Parameters
        ----------
        position: ndarray
            The position where to calculate the spatial structures needed.
            Shape (3,...). If position is `None` or not passed, it is assumed
            that the algorithm is bound to a position and `self.position` will be used.

        Returns
        -------
        sptaial_structures : dict
            Dictionary with the spatial structures required to fulfill the evaluation
            of the algorithm(s).

        Note
        ----
        Algorithm which are bound to a position will cache the spatial structures. It is
        therefore important to not manually change the position, since that will not clear the cache
        and the new position is not actually used.

        """
        # If called without a position we are using a bound algorithm, check the cache and calculate it if needed
        if position is None:
            try:
                return self._cached_spatial_structures
            except AttributeError:
                self._cached_spatial_structures = self._spatial_structures(self.position)
                return self._cached_spatial_structures
        # Check what spatial structures we need from the array to fulfill the requirements
        spatial_structures = {}
        for key, value in self.requires.items():
            if key.find('pressure_derivs') > -1:
                spatial_structures['pressure_derivs'] = max(value, spatial_structures.get('pressure_derivs', -1))
            elif key.find('spherical_harmonics') > -1:
                spatial_structures['spherical_harmonics'] = max(value, spatial_structures.get('spherical_harmonics', -1))
            elif key != 'complex_transducer_amplitudes':
                raise ValueError("Unknown requirement '{}'".format(key))
        # Replace the requests with values calculated by the array
        if 'pressure_derivs' in spatial_structures:
            spatial_structures['pressure_derivs'] = self.array.pressure_derivs(position, orders=spatial_structures['pressure_derivs'])
        if 'spherical_harmonics' in spatial_structures:
            spatial_structures['spherical_harmonics'] = self.array.spherical_harmonics(position, orders=spatial_structures['spherical_harmonics'])
        return spatial_structures

    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, weight):
        return self.__mul__(weight)

    def __str__(self, not_api_call=True):
        return self._str_format_spec.format(self)

    def __format__(self, format_spec):
        cls = self.__class__.__name__ + ': '
        weight = getattr(self, 'weight', None)
        pos = getattr(self, 'position', None)
        weight = ' * ' + str(weight) if weight is not None else ''
        pos = ' @ ' + str(pos) if pos is not None else ''
        return format_spec.replace('%cls', cls).replace('%weight', weight).replace('%position', pos)


class Algorithm(AlgorithmBase):
    """Primary class for single point, single algorithms.

    This is a wrapper class for `AlgorithmImplementation` to simplify the manipulation
    and evaluation of the implemented algorithms. Normally it is not necessary to manually
    create the wrapper, since it should be done automagically.
    Many properties are inherited from the underlying algorithm implementation, e.g.
    `ndim`, `array`, `values`, `jacobians`.

    Parameters
    ----------
    algorithm : `AlgorithmImplementation`
        The implemented algorithm to use for calculations.

    Methods
    -------
    +
        Adds this algorithm with another `Algorithm` or `AlgorithmPoint`.

        :return: `AlgorithmPoint`.
    *
        Weight the algorithm with a suitable weight.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `UnboundCostFunction`
    @
        Bind the algorithm to a point in space. The point needs to have
        3 elements in the first dimension.

        :return: `BoundAlgorithm`
    -
        Converts to a magnitude target algorithm.

        :return: `VectorAlgorithm`

    """

    _str_format_spec = '{:%cls%name}'
    _is_bound = False
    _is_cost = False

    def __init__(self, algorithm):
        self.algorithm = algorithm
        value_indices = ''.join(chr(ord('i') + idx) for idx in range(self.ndim))
        self._sum_str = value_indices + ', ' + value_indices + '...'
        self.requires = self.algorithm.values_require.copy()

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and self.algorithm == other.algorithm
            and self.array == other.array
        )

    @property
    def name(self):
        return self.algorithm.__class__.__name__

    @property
    def values(self):
        return self.algorithm.values

    @property
    def jacobians(self):
        return self.algorithm.jacobians

    @property
    def values_require(self):
        return self.algorithm.values_require

    @property
    def jacobians_require(self):
        return self.algorithm.jacobians_require

    @property
    def ndim(self):
        return self.algorithm.ndim

    @property
    def array(self):
        return self.algorithm.array

    def __call__(self, complex_transducer_amplitudes, position):
        """Evaluate the algorithm implementation.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.
        position : array-like
            The position(s) where to evaluate the algorithm.
            The first dimension needs to have 3 elements.

        Returns
        -------
        values: ndarray
            The values of the implemented algorithm used to create the wrapper.

        """
        # Prepare the requirements dict
        spatial_structures = self._spatial_structures(position)
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        # Call the function with the correct arguments
        return self.values(**{key: requirements[key] for key in self.values_require})

    def __add__(self, other):
        if other == 0:
            return self
        if type(self) == type(other):
            return AlgorithmPoint(self, other)
        else:
            return NotImplemented

    def __sub__(self, vector):
        return VectorAlgorithm(algorithm=self, target_vector=vector)

    def __mul__(self, weight):
        weight = np.asarray(weight)
        if weight.dtype == object:
            return NotImplemented
        return UnboundCostFunction(weight=weight, algorithm=self.algorithm)

    def __matmul__(self, position):
        position = np.asarray(position)
        if position.ndim < 1 or position.shape[0] != 3:
            return NotImplemented
        return BoundAlgorithm(position=position, algorithm=self.algorithm)

    def __format__(self, format_spec):
        name = getattr(self, 'name', None) or 'Unknown'
        return super().__format__(format_spec.replace('%name', name))


class BoundAlgorithm(Algorithm):
    """Position-bound class for single point, single algorithms.

    See `Algorithm` for more precise description.

    Parameters
    ----------
    algorithm : AlgorithmImplementation
        The implemented algorithm to use for calculations.
    position : numpy.ndarray
        The position to bind to.

    Methods
    -------
    +
        Adds this algorithm with another `BoundAlgorithm`,
        `BoundAlgorithmPoint`, or `AlgorithmCollection`.

        :return: `BoundAlgorithmPoint` or `AlgorithmCollection`.
    *
        Weight the algorithm with a suitable weight.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `CostFunction`
    @
        Re-bind the algorithm to a new point in space. The point needs to have
        3 elements in the first dimension.

        :return: `BoundAlgorithm`
    -
        Converts to a magnitude target algorithm.

        :return: `VectorBoundAlgorithm`

    """

    _str_format_spec = '{:%cls%name%position}'
    _is_bound = True
    _is_cost = False

    def __init__(self, algorithm, position, **kwargs):
        super().__init__(algorithm=algorithm, **kwargs)
        self.position = position

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and np.allclose(self.position, other.position)
        )

    def __call__(self, complex_transducer_amplitudes):
        """Evaluate the algorithm implementation.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.

        Returns
        -------
        values: ndarray
            The values of the implemented algorithm used to create the wrapper.

        """
        spatial_structures = self._spatial_structures()
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        return self.values(**{key: requirements[key] for key in self.values_require})

    def __add__(self, other):
        if other == 0:
            return self
        if type(self) == type(other):
            if np.allclose(self.position, other.position):
                return BoundAlgorithmPoint(self, other)
            else:
                return AlgorithmCollection(self, other)
        else:
            return NotImplemented

    def __sub__(self, vector):
        return VectorBoundAlgorithm(algorithm=self, target_vector=vector, position=self.position)

    def __mul__(self, weight):
        weight = np.asarray(weight)
        if weight.dtype == object:
            return NotImplemented
        return CostFunction(weight=weight, position=self.position, algorithm=self.algorithm)


class UnboundCostFunction(Algorithm):
    """Unbound cost functions for single point, single algorithms.

    See `Algorithm` for more precise description.

    Parameters
    ----------
    algorithm : AlgorithmImplementation
        The implemented algorithm to use for calculations.
    weight : numpy.ndarray
        The weight to use for the summation of values. Needs to have the same
        number of dimensions as the `AlgorithmImplementation` used.

    Methods
    -------
    +
        Adds this algorithm with another `UnboundCostFunction` or `UnboundCostFunctionPoint`.

        :return: `UnboundCostFunctionPoint`.
    *
        Rescale the weight, i.e. multiplies the current weight with the new value.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `UnboundCostFunction`
    @
        Bind the algorithm to a point in space. The point needs to have
        3 elements in the first dimension.

        :return: `CostFunction`
    -
        Converts to a magnitude target algorithm.

        :return: `VectorUnboundCostFunction`

    """

    _str_format_spec = '{:%cls%name%weight}'
    _is_bound = False
    _is_cost = True

    def __init__(self, algorithm, weight, **kwargs):
        super().__init__(algorithm=algorithm, **kwargs)
        self.weight = np.asarray(weight)
        if self.weight.ndim < self.ndim:
            extra_dims = self.ndim - self.weight.ndim
            self.weight.shape = (1,) * extra_dims + self.weight.shape
        for key, value in self.jacobians_require.items():
            self.requires[key] = max(value, self.requires.get(key, -1))

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and np.allclose(self.weight, other.weight)
        )

    def __call__(self, complex_transducer_amplitudes, position):
        """Evaluate the algorithm implementation.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.
        position : array-like
            The position(s) where to evaluate the algorithm.
            The first dimension needs to have 3 elements.

        Returns
        -------
        values: ndarray
            The values of the implemented algorithm used to create the wrapper.
        jacobians : ndarray
            The jacobians of the values with respect to the transducers.

        """
        spatial_structures = self._spatial_structures(position)
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        values = self.values(**{key: requirements[key] for key in self.values_require})
        jacobians = self.jacobians(**{key: requirements[key] for key in self.jacobians_require})
        return np.einsum(self._sum_str, self.weight, values), np.einsum(self._sum_str, self.weight, jacobians)

    def __add__(self, other):
        if other == 0:
            return self
        if type(self) == type(other):
            return UnboundCostFunctionPoint(self, other)
        else:
            return NotImplemented

    def __sub__(self, vector):
        return VectorUnboundCostFunction(algorithm=self, target_vector=vector, weight=self.weight)

    def __mul__(self, weight):
        weight = np.asarray(weight)
        if weight.dtype == object:
            return NotImplemented
        return UnboundCostFunction(self.algorithm, self.weight * weight)

    def __matmul__(self, position):
        position = np.asarray(position)
        if position.ndim < 1 or position.shape[0] != 3:
            return NotImplemented
        return CostFunction(weight=self.weight, position=position, algorithm=self.algorithm)


class CostFunction(UnboundCostFunction, BoundAlgorithm):
    """Cost functions for single point, single algorithms.

    See `Algorithm` for more precise description.

    Parameters
    ----------
    algorithm : AlgorithmImplementation
        The implemented algorithm to use for calculations.
    weight : numpy.ndarray
        The weight to use for the summation of values. Needs to have the same
        number of dimensions as the `AlgorithmImplementation` used.
    position : numpy.ndarray
        The position to bind to.

    Methods
    -------
    +
        Adds this algorithm with another `CostFunction`,
        `CostFunctionPoint`, or `CostFunctionCollection`.

        :return: `CostFunctionPoint`,or `CostFunctionCollection`
    *
        Rescale the weight, i.e. multiplies the current weight with the new value.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `CostFunction`
    @
        Re-bind the algorithm to a new point in space. The point needs to have
        3 elements in the first dimension.

        :return: `CostFunction`
    -
        Converts to a magnitude target algorithm.

        :return: `VectorCostFunction`

    """

    _str_format_spec = '{:%cls%name%weight%position}'
    _is_bound = True
    _is_cost = True

    # Inheritance order is important here, we need to resolve to UnboundCostFunction.__mul__ and not BoundAlgorithm.__mul__
    def __init__(self, algorithm, weight, position, **kwargs):
        super().__init__(algorithm=algorithm, weight=weight, position=position, **kwargs)

    def __eq__(self, other):
        return super().__eq__(other)

    def __call__(self, complex_transducer_amplitudes):
        """Evaluate the algorithm implementation.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.

        Returns
        -------
        values: ndarray
            The values of the implemented algorithm used to create the wrapper.
        jacobians : ndarray
            The jacobians of the values with respect to the transducers.

        """
        spatial_structures = self._spatial_structures()
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        values = self.values(**{key: requirements[key] for key in self.values_require})
        jacobians = self.jacobians(**{key: requirements[key] for key in self.jacobians_require})
        return np.einsum(self._sum_str, self.weight, values), np.einsum(self._sum_str, self.weight, jacobians)

    def __add__(self, other):
        if other == 0:
            return self
        if type(self) == type(other):
            if np.allclose(self.position, other.position):
                return CostFunctionPoint(self, other)
            else:
                return CostFunctionCollection(self, other)
        else:
            return NotImplemented

    def __sub__(self, vector):
        return VectorCostFunction(algorithm=self, target_vector=vector, weight=self.weight, position=self.position)

    def __mul__(self, weight):
        weight = np.asarray(weight)
        if weight.dtype == object:
            return NotImplemented
        return CostFunction(self.algorithm, self.weight * weight, self.position)


class VectorBase(Algorithm):
    """Base class for magnitude target algorithms.

    Uses an algorithm  :math:`A` to instead calculate :math:`V = |A - A_0|^2`,
    i.e. the squared magnitude difference to a target. For multi-dimensional algorithms
    the target needs to have the same (or a broadcastable) shape.
    The jacobians are calculated as :math:`dV = 2 dA (A-A_0)`.

    Parameters
    ----------
    algorithm: Algorithm-like
        A wrapper of an algorithm implementation, of the same type as the magnitude target.
    target_vector: numpy.ndarray
        The static offset target value(s).

    Note
    ----
    This class should not be instantiated directly, only use subclasses.

    """

    def __init__(self, algorithm, target_vector, **kwargs):
        if type(self) == VectorBase:
            raise AssertionError('`VectorBase` should never be directly instantiated!')
        self.values_require = algorithm.values_require.copy()
        self.jacobians_require = algorithm.jacobians_require.copy()
        for key, value in algorithm.values_require.items():
            self.jacobians_require[key] = max(value, self.jacobians_require.get(key, -1))
        super().__init__(algorithm=algorithm, **kwargs)
        target_vector = np.asarray(target_vector)
        self.target_vector = target_vector

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and np.allclose(self.target_vector, other.target_vector)
        )

    @property
    def name(self):
        return self.algorithm.name

    def values(self, **kwargs):
        """Calculate squared magnitude difference.

        If the underlying algorithm returns :math:`A`, this function returns
        :math:`|A - A_0|^2`, where :math:`A_0` is the target value.

        For information about parameters, see the documentation of the values function
        of the underlying objects, accessed through the `algorithm` properties.
        """
        values = self.algorithm.values(**kwargs)
        values -= self.target_vector.reshape([-1] + (values.ndim - 1) * [1])
        return np.real(values * np.conj(values))

    def jacobians(self, **kwargs):
        """Calculate jacobians squared magnitude difference.

        If the underlying algorithm returns :math:`dA`, the derivative of the value(s)
        with respect to the transducers, this function returns
        :math:`2 dA (A - A_0)`, where :math:`A_0` is the target value.

        For information about parameters, see the documentation of the values function
        of the underlying objects, accessed through the `algorithm` properties.
        """
        values = self.algorithm.values(**{key: kwargs[key] for key in self.algorithm.values_require})
        values -= self.target_vector.reshape([-1] + (values.ndim - 1) * [1])
        jacobians = self.algorithm.jacobians(**{key: kwargs[key] for key in self.algorithm.jacobians_require})
        return 2 * jacobians * values.reshape(values.shape[:self.ndim] + (1,) + values.shape[self.ndim:])

    # These properties are needed to not overwrite the requirements defined in the algorithm implementations.
    @property
    def values_require(self):
        return self._values_require

    @values_require.setter
    def values_require(self, val):
        self._values_require = val

    @property
    def jacobians_require(self):
        return self._jacobians_require

    @jacobians_require.setter
    def jacobians_require(self, val):
        self._jacobians_require = val

    def __sub__(self, vector):
        kwargs = {}
        if self._is_bound:
            kwargs['position'] = self.position
        if self._is_cost:
            kwargs['weight'] = self.weight
        return type(self)(self.algorithm, self.target_vector + vector, **kwargs)

    def __format__(self, format_spec):
        format_spec = format_spec.replace('%name', '||%name - %vector||^2').replace('%vector', str(self.target_vector))
        return super().__format__(format_spec)


class VectorAlgorithm(VectorBase, Algorithm):
    """Magnitude target algorithm class.

    Calculates the squared magnitude difference between the algorithm value(s)
    and a static target value(s).

    Parameters
    ----------
    algorithm: Algorithm
        A wrapper of an algorithm implementation.
    target_vector: numpy.ndarray
        The static offset target value(s).

    Methods
    -------
    +
        Adds this algorithm with another `Algorithm` or `AlgorithmPoint`.

        :return: `AlgorithmPoint`
    *
        Weight the algorithm with a suitable weight.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `VectorUnboundCostFunction`
    @
        Bind the algorithm to a point in space. The point needs to have
        3 elements in the first dimension.

        :return: `VectorBoundAlgorithm`
    -
        Shifts the current target value(s) with the new values.

        :return: `VectorAlgorithm`

    """

    def __add__(self, other):
        if other == 0:
            return self
        other_type = type(other)
        if VectorBase in other_type.__bases__:
            other_type = other_type.__bases__[1]
        if other_type == type(self).__bases__[1]:
            return AlgorithmPoint(self, other)
        else:
            return NotImplemented

    def __matmul__(self, position):
        algorithm = self.algorithm @ position
        return VectorBoundAlgorithm(algorithm=algorithm, target_vector=self.target_vector, position=algorithm.position)

    def __mul__(self, weight):
        algorithm = self.algorithm * weight
        return VectorUnboundCostFunction(algorithm=algorithm, target_vector=self.target_vector, weight=algorithm.weight)


class VectorBoundAlgorithm(VectorBase, BoundAlgorithm):
    """Magnitude target bound algorithm class.

    Calculates the squared magnitude difference between the algorithm value(s)
    and a static target value(s).

    Parameters
    ----------
    algorithm: BoundAlgorithm
        A wrapper of an algorithm implementation.
    target_vector: numpy.ndarray
        The static offset target value(s).

    Methods
    -------
    +
        Adds this algorithm with another `BoundAlgorithm`,
        `BoundAlgorithmPoint`, or `AlgorithmCollection`.

        :return: `BoundAlgorithmPoint`, or `AlgorithmCollection`
    *
        Weight the algorithm with a suitable weight.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `VectorCostFunction`
    @
        Re-bind the algorithm to a point in space. The point needs to have
        3 elements in the first dimension.

        :return: `VectorBoundAlgorithm`
    -
        Shifts the current target value(s) with the new values.

        :return: `BoundVectorAlgorithm`

    """

    def __add__(self, other):
        if other == 0:
            return self
        other_type = type(other)
        if VectorBase in other_type.__bases__:
            other_type = other_type.__bases__[1]
        if other_type == type(self).__bases__[1]:
            if np.allclose(self.position, other.position):
                return BoundAlgorithmPoint(self, other)
            else:
                return AlgorithmCollection(self, other)
        else:
            return NotImplemented

    def __matmul__(self, position):
        algorithm = self.algorithm @ position
        return VectorBoundAlgorithm(algorithm=algorithm, target_vector=self.target_vector, position=algorithm.position)

    def __mul__(self, weight):
        algorithm = self.algorithm * weight
        return VectorCostFunction(algorithm=algorithm, target_vector=self.target_vector, weight=algorithm.weight, position=algorithm.position)


class VectorUnboundCostFunction(VectorBase, UnboundCostFunction):
    """Magnitude target unbound cost function class.

    Calculates the squared magnitude difference between the algorithm value(s)
    and a static target value(s).

    Parameters
    ----------
    algorithm: UnboundCostFunction
        A wrapper of an algorithm implementation.
    target_vector: numpy.ndarray
        The static offset target value(s).

    Methods
    -------
    +
        Adds this algorithm with another `UnboundCostFunction` or `UnboundCostFunctionPoint`.

        :return: `UnboundCostFunctionPoint`
    *
        Rescale the weight, i.e. multiplies the current weight with the new value.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `VectorUnboundCostFunction`
    @
        Bind the algorithm to a point in space. The point needs to have
        3 elements in the first dimension.

        :return: `VectorCostFunction`
    -
        Shifts the current target value(s) with the new values.

        :return: `VectorUnboundCostFunction`

    """

    def __add__(self, other):
        if other == 0:
            return self
        other_type = type(other)
        if VectorBase in other_type.__bases__:
            other_type = other_type.__bases__[1]
        if other_type == type(self).__bases__[1]:
            return UnboundCostFunctionPoint(self, other)
        else:
            return NotImplemented

    def __matmul__(self, position):
        algorithm = self.algorithm @ position
        return VectorCostFunction(algorithm=algorithm, target_vector=self.target_vector, position=algorithm.position, weight=algorithm.weight)

    def __mul__(self, weight):
        algorithm = self.algorithm * weight
        return VectorUnboundCostFunction(algorithm=algorithm, target_vector=self.target_vector, weight=algorithm.weight)


class VectorCostFunction(VectorBase, CostFunction):
    """Magnitude target cost function class.

    Calculates the squared magnitude difference between the algorithm value(s)
    and a static target value(s).

    Parameters
    ----------
    algorithm: CostFunction
        A wrapper of an algorithm implementation.
    target_vector: numpy.ndarray
        The static offset target value(s).

    Methods
    -------
    +
        Adds this algorithm with another `CostFunction`,
        `CostFunctionPoint`, or `CostFunctionCollection`.

        :return: `CostFunctionPoint`, or `CostFunctionCollection`
    *
        Rescale the weight, i.e. multiplies the current weight with the new value.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `VectorCostFunction`
    @
        Bind the algorithm to a point in space. The point needs to have
        3 elements in the first dimension.

        :return: `VectorCostFunction`
    -
        Shifts the current target value(s) with the new values.

        :return: `VectorCostFunction`

    """

    def __add__(self, other):
        if other == 0:
            return self
        other_type = type(other)
        if VectorBase in other_type.__bases__:
            other_type = other_type.__bases__[1]
        if other_type == type(self).__bases__[1]:
            if np.allclose(self.position, other.position):
                return CostFunctionPoint(self, other)
            else:
                return CostFunctionCollection(self, other)
        else:
            return NotImplemented

    def __matmul__(self, position):
        algorithm = self.algorithm @ position
        return VectorCostFunction(algorithm=algorithm, target_vector=self.target_vector, position=algorithm.position, weight=algorithm.weight)

    def __mul__(self, weight):
        algorithm = self.algorithm * weight
        return VectorCostFunction(algorithm=algorithm, target_vector=self.target_vector, weight=algorithm.weight, position=algorithm.position)


class AlgorithmPoint(AlgorithmBase):
    """Class for multiple algorithm, single position calculations.

    This class collects multiple `Algorithm` objects for simultaneous evaluation at
    the same position(s). Since the algorithms can use the same spatial structures
    this is more efficient than to evaluate all the algorithms one by one.

    Parameters
    ----------
    *algorithms : Algorithm
        Any number of `Algorithm` objects.

    Methods
    -------
    +
        Adds an `Algorithm` or `AlgorithmPoint` to the current set
        of algorithms.

        :return: `AlgorithmPoint`
    *
        Weights all algorithms with the same weight. This requires
        that all the algorithms can actually use the same weight.

        :return: `UnboundCostFunctionPoint`
    @
        Binds all the algorithms to the same position.

        :return: `BoundAlgorithmPoint`
    -
        Converts all the algorithms to magnitude target algorithms.
        This requires that all the algorithms can use the same target.

        :return: `AlgorithmPoint`

    """

    _str_format_spec = '{:%cls%algorithms%position}'
    _is_bound = False
    _is_cost = False

    def __init__(self, *algorithms):
        self.algorithms = []
        self.requires = {}
        for algorithm in algorithms:
            self += algorithm

    def __eq__(self, other):
        return super().__eq__(other) and self.algorithms == other.algorithms

    @property
    def array(self):
        return self.algorithms[0].array

    def __call__(self, complex_transducer_amplitudes, position):
        """Evaluate all algorithms.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.
        position : array-like
            The position(s) where to evaluate the algorithms.
            The first dimension needs to have 3 elements.

        Returns
        -------
        values: list
            A list of the return values from the individual algorithms.
            Depending on the number of dimensions of the algorithms, the
            arrays in the list might not have compatible shapes.

        """
        # Prepare the requirements dict
        spatial_structures = self._spatial_structures(position)
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        # Call the function with the correct arguments
        return [algorithm.values(**{key: requirements[key] for key in algorithm.values_require}) for algorithm in self.algorithms]

    def __add__(self, other):
        if other == 0:
            return self
        if type(self) == type(other):
            return AlgorithmPoint(*self.algorithms, *other.algorithms)
        elif self._type == other._type:
            return AlgorithmPoint(*self.algorithms, other)
        else:
            return NotImplemented

    def __iadd__(self, other):
        add_element = False
        add_point = False
        if type(self) == type(other):
            add_point = True
        elif self._type == other._type:
            add_element = True
        old_requires = self.requires.copy()
        if add_element:
            for key, value in other.requires.items():
                self.requires[key] = max(value, self.requires.get(key, -1))
            self.algorithms.append(other)
        elif add_point:
            for algorithm in other.algorithms:
                self += algorithm
        else:
            return NotImplemented
        if self.requires != old_requires:
            # We have new requirements, if there are cached spatial structures they will
            # need to be recalculated at next call.
            try:
                del self._cached_spatial_structures
            except AttributeError:
                pass
        return self

    def __sub__(self, other):
        return type(self)(*[algorithm - other for algorithm in self.algorithms])

    def __mul__(self, weight):
        return UnboundCostFunctionPoint(*[algorithm * weight for algorithm in self.algorithms])

    def __matmul__(self, position):
        return BoundAlgorithmPoint(*[algorithm @ position for algorithm in self.algorithms])

    def __format__(self, format_spec):
        if '%algorithms' in format_spec:
            alg_start = format_spec.find('%algorithms')
            if len(format_spec) > alg_start + 11 and format_spec[alg_start + 11] == ':':
                alg_spec_len = format_spec[alg_start + 12].find(':')
                alg_spec = format_spec[alg_start + 12:alg_start + 12 + alg_spec_len]
                pre = format_spec[:alg_start + 10]
                post = format_spec[alg_start + 13 + alg_spec_len:]
                format_spec = pre + post
            else:
                alg_spec = '{:%name%weight}'
            alg_str = '('
            for algorithm in self.algorithms:
                alg_str += alg_spec.format(algorithm) + ' + '
            format_spec = format_spec.replace('%algorithms', alg_str.rstrip(' + ') + ')')
        return super().__format__(format_spec.replace('%name', ''))


class BoundAlgorithmPoint(AlgorithmPoint):
    """Class for multiple algorithm, single fixed position calculations.

    This class collects multiple `BoundAlgorithm` bound to the same position(s)
    for simultaneous evaluation. Since the algorithms can use the same spatial
    structures this is more efficient than to evaluate all the algorithms one by one.

    Parameters
    ----------
    *algorithms : BoundAlgorithm
        Any number of `BoundAlgorithm` objects.

    Warning
    --------
    If the class is initialized with algorithms bound to different points,
    some of the algorithms are simply discarded.

    Methods
    -------
    +
        Adds an `BoundAlgorithm` or `BoundAlgorithmPoint` to the current set
        of algorithms. If the newly added algorithm is not bound to the same position,
        an `AlgorithmCollection` will be created and returned.

        :return: `BoundAlgorithmPoint` or `AlgorithmCollection`
    *
        Weights all algorithms with the same weight. This requires
        that all the algorithms can actually use the same weight.

        :return: `CostFunctionPoint`
    @
        Re-binds all the algorithms to a new position.

        :return: `BoundAlgorithmPoint`
    -
        Converts all the algorithms to magnitude target algorithms.
        This requires that all the algorithms can use the same target.

        :return: `BoundAlgorithmPoint`

    """

    _is_bound = True
    _is_cost = False

    def __init__(self, *algorithms):
        self.position = algorithms[0].position
        super().__init__(*algorithms)

    def __call__(self, complex_transducer_amplitudes):
        """Evaluate all algorithms.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.

        Returns
        -------
        values: list
            A list of the return values from the individual algorithms.
            Depending on the number of dimensions of the algorithms, the
            arrays in the list might not have compatible shapes.

        """
        spatial_structures = self._spatial_structures()
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        return [algorithm.values(**{key: requirements[key] for key in algorithm.values_require}) for algorithm in self.algorithms]

    def __add__(self, other):
        if other == 0:
            return self
        if self._type != other._type:
            return NotImplemented
        if type(other) == BoundAlgorithmPoint and np.allclose(self.position, other.position):
            return BoundAlgorithmPoint(*self.algorithms, *other.algorithms)
        elif isinstance(other, BoundAlgorithm) and np.allclose(self.position, other.position):
            return BoundAlgorithmPoint(*self.algorithms, other)
        else:
            return AlgorithmCollection(self, other)

    def __iadd__(self, other):
        try:
            if np.allclose(other.position, self.position):
                return super().__iadd__(other)
            else:
                return AlgorithmCollection(self, other)
        except AttributeError:
            return NotImplemented

    def __mul__(self, weight):
        return CostFunctionPoint(*[algorithm * weight for algorithm in self.algorithms])


class UnboundCostFunctionPoint(AlgorithmPoint):
    """Class for multiple cost function, single position calculations.

    This class collects multiple `UnboundCostFunction` objects for simultaneous evaluation at
    the same position(s). Since the algorithms can use the same spatial structures
    this is more efficient than to evaluate all the algorithms one by one.

    Parameters
    ----------
    *algorithms : UnboundCostFunction
        Any number of `UnboundCostFunction` objects.

    Methods
    -------
    +
        Adds an `UnboundCostFunction` or `UnboundCostFunctionPoint` to the 
        current set of algorithms.

        :return: `UnboundCostFunctionPoint`
    *
        Rescale the weights of all algorithms, i.e. multiplies the current set of 
        weight with the new value. The weight needs to have the correct number of
        dimensions, but will otherwise broadcast properly.

        :return: `UnboundCostFunctionPoint`
    @
        Binds all the algorithms to the same position.

        :return: `CostFunctionPoint`
    -
        Converts all the algorithms to magnitude target algorithms.
        This requires that all the algorithms can use the same target.

        :return: `UnboundCostFunctionPoint`

    """

    _is_bound = False
    _is_cost = True

    def __call__(self, complex_transducer_amplitudes, position):
        """Evaluate the all cost functions.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.
        position : array-like
            The position(s) where to evaluate the algorithm.
            The first dimension needs to have 3 elements.

        Returns
        -------
        values: ndarray
            The summed values of all cost functions.
        jacobians : ndarray
            The the summed jacobians of all cost functions.

        """
        spatial_structures = self._spatial_structures(position)
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        value = 0
        jacobians = 0
        for algorithm in self.algorithms:
            value += np.einsum(algorithm._sum_str, algorithm.weight, algorithm.values(**{key: requirements[key] for key in algorithm.values_require}))
            jacobians += np.einsum(algorithm._sum_str, algorithm.weight, algorithm.jacobians(**{key: requirements[key] for key in algorithm.jacobians_require}))
        return value, jacobians

    def __add__(self, other):
        if other == 0:
            return self
        if type(self) == type(other):
            return UnboundCostFunctionPoint(*self.algorithms, *other.algorithms)
        elif self._type == other._type:
            return UnboundCostFunctionPoint(*self.algorithms, other)
        else:
            return NotImplemented

    def __matmul__(self, position):
        return CostFunctionPoint(*[algorithm @ position for algorithm in self.algorithms])


class CostFunctionPoint(UnboundCostFunctionPoint, BoundAlgorithmPoint):
    """Class for multiple cost function, single fixed position calculations.

    This class collects multiple `CostFunction` bound to the same position(s)
    for simultaneous evaluation. Since the algorithms can use the same spatial
    structures this is more efficient than to evaluate all the algorithms one by one.

    Parameters
    ----------
    *algorithms : CostFunction
        Any number of `CostFunction` objects.

    Warning
    --------
    If the class is initialized with algorithms bound to different points,
    some of the algorithms are simply discarded.

    Methods
    -------
    +
        Adds an `CostFunction` or `CostFunctionPoint` to the  current set of algorithms. 
        If the newly added algorithm is not bound to the same position,
        a `CostFunctionCollection` will be created and returned.

        :return: `CostFunctionPoint` or `CostFunctionCollection`
    *
        Rescale the weights of all algorithms, i.e. multiplies the current set of 
        weight with the new value. The weight needs to have the correct number of
        dimensions, but will otherwise broadcast properly.

        :return: `CostFunctionPoint`
    @
        Re-binds all the algorithms to a new position.

        :return: `CostFunctionPoint`
    -
        Converts all the algorithms to magnitude target algorithms.
        This requires that all the algorithms can use the same target.

        :return: `CostFunctionPoint`

    """

    _is_bound = True
    _is_cost = True

    def __call__(self, complex_transducer_amplitudes):
        """Evaluate the all cost functions.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.

        Returns
        -------
        values: ndarray
            The summed values of all cost functions.
        jacobians : ndarray
            The the summed jacobians of all cost functions.

        """
        spatial_structures = self._spatial_structures()
        requirements = self._evaluate_requirements(complex_transducer_amplitudes, spatial_structures)
        value = 0
        jacobians = 0
        for algorithm in self.algorithms:
            value += np.einsum(algorithm._sum_str, algorithm.weight, algorithm.values(**{key: requirements[key] for key in algorithm.values_require}))
            jacobians += np.einsum(algorithm._sum_str, algorithm.weight, algorithm.jacobians(**{key: requirements[key] for key in algorithm.jacobians_require}))
        return value, jacobians

    def __add__(self, other):
        if other == 0:
            return self
        if self._type != other._type:
            return NotImplemented
        if type(other) == CostFunctionPoint and np.allclose(self.position, other.position):
            return CostFunctionPoint(*self.algorithms, *other.algorithms)
        elif isinstance(other, CostFunction) and np.allclose(self.position, other.position):
            return CostFunctionPoint(*self.algorithms, other)
        else:
            return CostFunctionCollection(self, other)

    def __iadd__(self, other):
        try:
            if np.allclose(other.position, self.position):
                return super().__iadd__(other)
            else:
                return CostFunctionCollection(self, other)
        except AttributeError:
            return NotImplemented


class AlgorithmCollection(AlgorithmBase):
    """Collects algorithms bound to different positions.

    Convenience class to evaluate and manipulate algorithms bound to
    different positions in space. Will not improve the computational
    efficiency beyond the gains from merging the algorithms bound
    to the same positions.

    Parameters
    ----------
    *algorithms: BoundAlgorithm or BoundAlgorithmPoint
        Any number of algorithms bound to any number of points.

    Methods
    -------
    +
        Adds an additional `BoundAlgorithm`, `BoundAlgorithmPoint`
        or `AlgorithmCollection` to the set.

        :return: `AlgorithmCollection`
    *
        Weights all algorithms in the set with the same weight.
        Requires that they can actually be weighted with the same
        weight.

        :return: `CostFuncitonCollection`

    """

    _str_format_spec = '{:%cls%points}'
    _is_bound = True
    _is_cost = False

    def __init__(self, *algorithms):
        self.algorithms = []
        for algorithm in algorithms:
            self += algorithm

    def __eq__(self, other):
        return super().__eq__(other) and self.algorithms == other.algorithms

    def __call__(self, complex_transducer_amplitudes):
        """Evaluate all algorithms.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.

        Returns
        -------
        values: list
            A list of the return values from the individual algorithms.
            Depending on the number of dimensions of the algorithms, the
            arrays in the list might not have compatible shapes, and some
            might be lists with values corresponding to the same point in space.

        """
        values = []
        for point in self.algorithms:
            values.append(point(complex_transducer_amplitudes))
        return values

    def __add__(self, other):
        if other == 0:
            return self
        elif self._type != other._type:
            return NotImplemented
        else:
            return type(self)(*self.algorithms, other)

    def __iadd__(self, other):
        if type(other) == type(self):
            for algorithm in other.algorithms:
                self += algorithm
            return self
        elif self._type != other._type:
            return NotImplemented
        else:
            for idx, point in enumerate(self.algorithms):
                if np.allclose(point.position, other.position):
                    # Mutating `point` will not update the contents in the list!
                    self.algorithms[idx] += other
                    break
            else:
                self.algorithms.append(other)
            return self

    def __mul__(self, weight):
        return CostFunctionCollection(*[algorithm * weight for algorithm in self.algorithms])

    def __format__(self, format_spec):
        if '%points' in format_spec:
            points_start = format_spec.find('%points')
            if len(format_spec) > points_start + 7 and format_spec[points_start + 7] == ':':
                points_spec_len = format_spec[points_start + 8].rind(':')
                points_spec = format_spec[points_start + 8:points_start + 8 + points_spec_len]
                pre = format_spec[:points_start + 6]
                post = format_spec[points_start + 9 + points_spec_len:]
                format_spec = pre + post
            else:
                points_spec = '\t{:%cls%name%algorithms%weight%position}\n'
            points_str = '[\n'
            for algorithm in self.algorithms:
                points_str += points_spec.format(algorithm).replace('%algorithms', '')
            format_spec = format_spec.replace('%points', points_str + ']')
        return super().__format__(format_spec)


class CostFunctionCollection(AlgorithmCollection, CostFunctionPoint):
    """Collects cost functions bound to different positions.

    Convenience class to evaluate and manipulate cost functions bound to
    different positions in space. Will not improve the computational
    efficiency beyond the gains from merging the algorithms bound
    to the same positions.

    Parameters
    ----------
    *algorithms: CostFunction or CostFunctionPoint
        Any number of cost functions bound to any number of points.

    Methods
    -------
    +
        Adds an additional `CostFunction`, `CostFunctionPoint`
        or `CostFunctionCollection` to the set.

        :return: `CostFunctionCollection`
    *
        Rescale the weights, i.e. multiplies the current weights with the new value.
        The weight needs to have the correct number of dimensions, but will
        otherwise broadcast properly.

        :return: `CostFuncitonCollection`

    """

    _is_bound = True
    _is_cost = True

    def __call__(self, complex_transducer_amplitudes):
        """Evaluate the all cost functions.

        Parameters
        ----------
        compelx_transducer_amplitudes : complex numpy.ndarray
            Complex representation of the transducer phases and amplitudes of the
            array used to create the algorithm.

        Returns
        -------
        values: ndarray
            The summed values of all cost functions.
        jacobians : ndarray
            The the summed jacobians of all cost functions.

        """
        values = 0
        jacobians = 0
        for algorithm in self.algorithms:
            val, jac = algorithm(complex_transducer_amplitudes)
            values += val
            jacobians += jac
        return values, jacobians
