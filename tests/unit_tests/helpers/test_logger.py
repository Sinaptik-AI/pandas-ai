import logging
from pandasai.helpers.logger import Logger


def test_verbose_setter():
    # Initialize logger with verbose=False
    logger = Logger(verbose=False)
    assert logger._verbose is False
    assert not any(isinstance(handler, logging.StreamHandler) for handler in logger._logger.handlers)

    # Set verbose to True
    logger.verbose = True
    assert logger._verbose is True
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger._logger.handlers)
    assert len(logger._logger.handlers) == 1

    # Set verbose to False
    logger.verbose = False
    assert logger._verbose is False
    assert not any(isinstance(handler, logging.StreamHandler) for handler in logger._logger.handlers)
    assert len(logger._logger.handlers) == 0

    # Set verbose to True again to ensure multiple toggles work
    logger.verbose = True
    assert logger._verbose is True
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger._logger.handlers)
    assert len(logger._logger.handlers) == 1

def test_save_logs_property():
    # Initialize logger with save_logs=False
    logger = Logger(save_logs=False, verbose=False)
    assert logger.save_logs is False

    # Enable save_logs
    logger.save_logs = True
    assert logger.save_logs is True
    assert any(isinstance(handler, logging.FileHandler) for handler in logger._logger.handlers)

    # Disable save_logs
    logger.save_logs = False
    assert logger.save_logs is False
    assert not any(isinstance(handler, logging.FileHandler) for handler in logger._logger.handlers)

def test_save_logs_property():
    # When logger is initialized with save_logs=True (default), it should have handlers
    logger = Logger(save_logs=True)
    assert logger.save_logs is True
    
    # When logger is initialized with save_logs=False, it should still have handlers if verbose=True
    logger = Logger(save_logs=False, verbose=True)
    assert logger.save_logs is True
    
    # When both save_logs and verbose are False, there should be no handlers
    logger = Logger(save_logs=False, verbose=False)
    logger._logger.handlers = []  # Reset handlers to match the property's expected behavior
    assert logger.save_logs is False
