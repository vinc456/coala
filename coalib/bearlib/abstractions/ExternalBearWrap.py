from functools import partial

from coalib.bears.LocalBear import LocalBear
from coala_decorators.decorators import enforce_signature
from coalib.misc.Shell import run_shell_command
from coalib.results.Diff import Diff
from coalib.results.Result import Result

def _create_wrapper(klass, options):
    class ExternalBearWrapBase(LocalBear):

        @staticmethod
        def get_executable():
            """
            Returns the executable of this class.

            :return:
                The executable name.
            """
            return options["executable"]

        def run(self, filename, file, **kwargs):
            out, err = run_shell_command(self.get_executable(), "Testing")
            yield Result.from_values(
                origin=self,
                message=out,
                file=filename,
                line=1,
                column=1,
                end_line=1,
                end_column=1)

    # Mixin the linter into the user-defined interface, otherwise
    # `create_arguments` and other methods would be overridden by the
    # default version.
    result_klass = type(klass.__name__, (klass, ExternalBearWrapBase), {})
    result_klass.__doc__ = klass.__doc__ if klass.__doc__ else ""
    return result_klass

@enforce_signature
def external_bear_wrap(executable: str,
           **options):

    options["executable"] = executable

    return partial(_create_wrapper, options=options)