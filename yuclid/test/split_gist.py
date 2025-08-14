#!/usr/bin/env python
import sys


def extract_segments(input_filepath, output_prefix="segment"):
    """
    Extracts segments from a text file. Each segment starts with a line
    beginning with "point" and ending with a line beginning with "prove".
    Each extracted segment is saved to a new text file.
    Multiple "point" lines can exist within a single segment.

    Args:
        input_filepath (str): The path to the input text file.
        output_prefix (str): The common prefix for the output filenames.
                             (e.g., "my_doc" will result in files like "my_doc_1.txt")
    """
    try:
        with open(input_filepath, "r") as infile:
            segment_content = []
            in_segment = False
            segment_count = 0

            for line_num, line in enumerate(infile, 1):
                # Check if the line starts a new segment or is another 'point' within a segment
                if line.strip().lower().startswith("point"):
                    # If we are not currently in a segment, start collecting.
                    # If we are already in a segment, this 'point' is part of the current segment.
                    if not in_segment:
                        in_segment = True
                    segment_content.append(line)  # Always include the "point" line

                # If inside a segment, append the current line
                elif in_segment:
                    segment_content.append(line)

                    # Check if the line ends the current segment
                    if line.strip().lower().startswith("prove"):
                        segment_count += 1
                        # Use the provided output_prefix
                        output_filename = f"{output_prefix}_{segment_count}.txt"
                        with open(output_filename, "w") as outfile:
                            outfile.writelines(segment_content)
                        print(f"Saved: {output_filename}")
                        segment_content = []  # Clear content for the next segment
                        in_segment = False

            # After the loop, check if there's an unfinished segment
            if in_segment and segment_content:
                print(
                    f"Warning: End of file reached, but segment {segment_count + 1} did not end with 'prove'. Saving incomplete segment."
                )
                segment_count += 1
                # Use the provided output_prefix
                output_filename = f"{output_prefix}_{segment_count}.txt"
                with open(output_filename, "w") as outfile:
                    outfile.writelines(segment_content)
                print(f"Saved: {output_filename}")

        if segment_count == 0:
            print("No segments found starting with 'point' and ending with 'prove'.")

    except FileNotFoundError:
        print(f"Error: Input file '{input_filepath}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python extract_segments.py <input_file.txt> [output_prefix]")
        print("  <input_file.txt> : The path to the input text file.")
        print(
            "  [output_prefix]  : Optional. The prefix for the output filenames (default: 'segment')."
        )
        sys.exit(1)

    input_file = sys.argv[1]
    # Check if a prefix is provided, otherwise use the default
    output_prefix = sys.argv[2] if len(sys.argv) == 3 else "segment"

    extract_segments(input_file, output_prefix)
