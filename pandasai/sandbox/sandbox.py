class Sandbox:
    def __init__(self):
        self.started = False

    def start(self):
        raise NotImplementedError("The start method must be implemented by subclasses.")

    def stop(self):
        raise NotImplementedError("The stop method must be implemented by subclasses.")

    def execute(self, code, dfs):
        if not self.started:
            self.start()
            try:
                result = self._exec_code(code, dfs)
            finally:
                self.stop()
            return result
        return self._exec_code(code, dfs)

    def _exec_code(self, code):
        raise NotImplementedError(
            "The exec_code method must be implemented by subclasses."
        )

    def pass_csv(self, csv_data):
        raise NotImplementedError(
            "The pass_csv method must be implemented by subclasses."
        )
