homepage_info <- function() {
    tags$div(
        h2("Celseq Sample Sheet Generator"),
        p("This dashboard executes a series of operations designed to streamline data processing and analysis for the Genomics Metadata Multiplexing Project. This dashboard streamlines the process of generating sample sheets and merging of flow cytometry data, to be used as input for downstream analysis."),
        p("The processing performed depends on the uploaded data, there are four scenarios that can be processed:"),
        tags$ul(
            tags$li(
                div(
                    h5("Scenario 1: Convert a plate template to a sample sheet", style = "font-weight: bold;"),
                    tags$b("Purpose:"), " Takes a colour-coded plate layout in Excel format and converts it into a row-wise spreadsheet.",
                    br(),
                    tags$b("Input:"), " To perform this operation only, upload a directory containing a sole Excel file with a plate layout with coloured wells.",
                    br(),
                    actionLink("viewOp1", "See sample Template file"),
                    br(),
                    tags$ul(
                      tags$li(
                        "The file name must include 'plate_layout' to be recognized.",
                      ),
                      tags$li(
                        "Each sheet name must contain the plate's name. Only one plate can be processed per sheet but one Excel file can contain multiple sheets.",
                      ),
                      tags$li(
                        "The process will find the layout grid by looking for plate number '1' diagonally right of the first cell 'A'.",
                      ),
                      tags$li(
                        "The colour key must appear under the plate layout, with each that is in the plate layout represented by a single colour.",
                      ),
                      tags$li(
                        "For downstream analysis, please make sure that the sample names match the sample names in your FCS files and primer spreadsheet."
                      ),
                    ),
                    tags$b("Output:"), " A sample sheet containing the following columns: plate number, well position, sample name."
                )
            ),
            tags$li(
                div(
                    h5("Scenario 2: Combine FCS Files into one document", style = "font-weight: bold;"),
                    tags$b("Purpose:"), " Merges multiple FCS files into a single TSV (Tab Separated Values) file using a vertical merge principle. This operation is essential for consolidating flow cytometry data.",
                    br(),
                    tags$b("Input:"), " To perform this operation only, upload a directory containing one or more FCS files only.",
                    br(),
                    tags$ul(
                      tags$li(
                        "The FCS file names must not contain any spaces and have the .fcs file extension."
                      ),
                      tags$li(
                        "For LCE plates, the sample name must be in the file name, between 'INX' and the plate name, separated by an underscore (e.g., '01Jan25_INX_Sample1_FCE123.fcs').",
                      ),
                      tags$li(
                        "For PRM plates, the sample name must be after the plate name, separated by an underscore (e.g., '01Jan25_INX_PRM123_Sample1.fcs').",
                      ),
                    ),
                    tags$b("Output:"), " A single TSV file containing merged data from all provided FCS files."
                )
            ),
            tags$li(
                div(
                    h5("Scenario 3: Combine FCS files and merge into spreadsheet", style = "font-weight: bold;"),
                    tags$b("Purpose:"), " Merges multiple FCS files as in Scenario 2, then merges the result into either a template spreadsheet or a provided sample sheet.",
                    br(),
                    tags$b("Input:"), " To perform this operation, upload a directory containing one or more FCS files with a template spreadsheet or ready-made sample sheet.",
                    br(),
                    actionLink("viewOp3", "See sample Template file"),
                    actionLink("viewOp4", "See sample Sample Sheet file"),
                    br(),
                    tags$ul(
                      tags$li(
                        "The FCS files must follow the naming conventions outlined in Scenario 2.",
                      ),
                      tags$li(
                        "If providing a template spreadsheet, it must be in Excel format and have 'template_sheet' in the file name.",
                      ),
                      tags$li(
                        "If providing a ready-made sample sheet, it must be in Excel format and have 'primer_template' in the file name.",
                      ),
                      tags$li(
                        "The template or sample sheet must contain a sheet that starts with 'sample primer'. This sheet's first column must be 'Plate#'. It also has to contain a column called 'Well position' and one of 'Sample', 'Sample name' or 'Sample type'."
                      ),
                    ),
                    tags$b("Output:"), " A single file that merges the aforementioned documents based on plate number, well position, and sample name."
                )
            ),
            tags$li(
                div(
                    h5("Scenario 4: Convert a plate template to a sample sheet and then merge into a template or sample sheet, optionally add FCS data.", style = "font-weight: bold;"),
                    tags$b("Purpose:"), " Creates a sample sheet from a plate spreadsheet as per Scenario 1, then optionally merges multiple FCS files as in Scenario 2, then merges the result into one spreadsheet as per Scenario 3.",
                    br(),
                    tags$b("Input:"), " To perform this operation, upload a directory containing zero or more FCS files with plate sheet and template sheet or ready-made spreadsheet.",
                    br(),
                    tags$ul(
                      tags$li(
                        "The plate spreadhsheet must follow the conventions outlined in Scenario 1.",
                      ),
                      tags$li(
                        "The FCS files (if provided) must follow the naming conventions outlined in Scenario 2.",
                      ),
                      tags$li(
                        "The template sheet or sample sheet must follow the conventions outlined in Scenario 3.",
                      ),
                    ),
                    tags$b("Output:"), " A single file that merges the aforementioned documents based on plate number, well position, and sample name."
                )
            ),
        ),
        tags$div(
            p("For more project information, please visit the ",
              a("Genomics Metadata Multiplexing GitHub", href = "https://github.com/WEHI-ResearchComputing/Genomics-Metadata-Multiplexing"),
              "."),
            p("Project wiki: ",
              a("WEHI-ResearchComputing/Genomics-Metadata-Multiplexing/wiki", href = "https://github.com/WEHI-ResearchComputing/Genomics-Metadata-Multiplexing/wiki"))
        ),
        style = "padding: 20px;"
    )
}
