from snippety import *

class SourceFileProcessor:

    def __init__(self, config):
        self.config = config
        self._output_lines = []
        self._inside_directive = False
        self._inside_generated_section = False
        self._current_directive = None

    def process_file(self, filepath):
        """Extracts the lines and directives from a file and writes the output
        back to it.
        """
        self._filepath = filepath
        self._current_line_number = 0
        for line in self._read_from_file(filepath):
            # If inside a directive (i.e _current_directive not None)
            # keep adding lines to that directive, unless it is start of new
            # directive, in which case we create a neste directive.
            # Once we've rolled back out of the nested directives, we call
            # _apply_directives, which adds the to the output lines or directs
            # To another file.
            self._current_line_number += 1
            if self._current_directive is not None:
                self._output_lines.append(line)
                if self._line_is_directive_start(line):
                    self._start_directive(line)
                elif self._line_is_inline_directive(line):
                    self._start_directive(line)
                    self._end_current_directive(line)
                elif self._line_is_directive_end(line):
                    self._end_current_directive(line)
                else:
                    self._current_directive.add_item(line)

            # If inside a generated section, do nothing other than check if
            # we've reached the end
            elif self._inside_generated_section:
                if self._line_is_generated_code_end(line):
                    self._inside_generated_section = False

            # If we're in normal code (not inside a directive or generated
            # section, we just check for starter of sections.
            else:
                if self._line_is_generated_code_start(line):
                    self._inside_generated_section = True
                else:
                    self._output_lines.append(line)
                    if self._line_is_directive_start(line):
                        self._start_directive(line)
                    elif self._line_is_inline_directive(line):
                        self._start_directive(line)
                        self._end_current_directive(line)

        #Fix, here call post-processing, and config for different files
        #Or check if file contents have changed...
        self._write_output(filepath)

    def _line_is_directive_start(self, line):
        line = line.strip()
        return line.startswith(self.config.directive_start_identifier)

    def _line_is_directive_end(self, line):
        line = line.strip()
        return line == self.config.directive_end_identifier

    def _line_is_inline_directive(self, line):
        return line.find(self.config.directive_inline_identifier) >= 0

    def _line_is_generated_code_start(self, line):
        line = line.strip()
        return line == self.config.output_start_identifier

    def _line_is_generated_code_end(self, line):
        line = line.strip()
        return line == self.config.output_end_identifier

    def _start_directive(self, line):
        print "Found directive: ", line.strip()
        try:
            new_directive = Directive(line, self.config)
        except DirectiveFormatError, e:
            raise FileParsingError(e, self._filepath, self._current_line_number)
        if self._current_directive:
            # We're within a directive, so nest it
            self._current_directive.add_item(new_directive)
        else:
            # Not within directive, so set it as to outtermost
            self._outtermost_directive = new_directive
        self._current_directive = new_directive

    def _end_current_directive(self, line):
        assert self._current_directive
        # outter_directive may be None, in which case we've reach the end
        self._current_directive = self._current_directive.outter_directive
        #If reached end of outtermost directive, apply directives
        if not self._current_directive:
            self._apply_directives()

    def _apply_directives(self):
        """Adds the output generated by the directive to the
        output line.
        Fix: all pre and post processing, as well as output to other file.
        """
        self._outtermost_directive.add_to_output_lines(self._output_lines)
        self._outtermost_directive = None

    def _write_output(self, output_path):
        self._write_to_file(output_path, self._output_lines)

    def _write_to_file(self, file, lines):
        f = open(file, 'w')
        f.write('\n'.join( [self._strip_new_line_chars(line) for line in lines]))
        f.close()

    def _strip_new_line_chars(self, line):
        return line.rstrip('\n')

    def _read_from_file(self, file):
        f = open(file, 'r')
        lines = [self._strip_new_line_chars(line) for line in f.readlines()]
        f.close()
        return lines
