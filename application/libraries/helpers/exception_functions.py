def api_assert_param(assertion, var):
    """This will raise an InvalidArgumentException when the assertion is False.

    Args:
        assertion (bool) : the assertion to assert
        var (str) : the name of the param to raise the exception with

    Raises:
        InvalidArgumentException :
    """
    if not assertion:
        raise ex400.InvalidArgumentException(str(var))
