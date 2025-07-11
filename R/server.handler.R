library(shiny)
library(shinyjs)
library(shinyalert)

source("R/ui.homepage.R")

# Thumbnail image handler function
thumbnail_image_handler <- function(input, output, session) {
    # Modal display functions for sample files
    observeEvent(input$viewOp1, {
        showModal(modalDialog(
            title = "Sample Plate Layout Sheet for Operation 1",
            tags$img(src = "https://github.com/WEHI-ResearchComputing/Genomics-Metadata-Multiplexing/blob/main/www/plate_layout.jpg?raw=true", style = "width:100%;"),
            easyClose = TRUE,
            footer = NULL
        ))
    })
    
    observeEvent(input$viewOp3, {
        showModal(modalDialog(
            title = "Sample Template Sheet for Operation 3",
            tags$img(src = "https://github.com/WEHI-ResearchComputing/Genomics-Metadata-Multiplexing/blob/main/www/template_sheet.jpg?raw=true", style = "width:100%;"),
            easyClose = TRUE,
            footer = NULL
        ))
    })
    
    observeEvent(input$viewOp4, {
        showModal(modalDialog(
            title = "Sample Primer Index File for Operation 4",
            tags$img(src = "https://github.com/WEHI-ResearchComputing/Genomics-Metadata-Multiplexing/blob/main/www/primer_index.jpg?raw=true", style = "width:100%;"),
            easyClose = TRUE,
            footer = NULL
        ))
    })
}

# Data download handler function
data_download_handler <- function(input, output, session, processedData) {
    output$downloadData <- downloadHandler(
        filename = function() {
            paste("processed-data-", Sys.Date(), ".", input$format, sep = "")
        },
        content = function(file) {
            # Depending on the selected format, write the processed data to the file
            if (input$format == "csv") {
                write.csv(processedData(), file, row.names = FALSE)
            } else if (input$format == "tsv") {
                write.table(processedData(), file, sep = "\t", row.names = FALSE)
            } else if (input$format == "xlsx") {
                # Assuming you have the 'writexl' package for Excel files
                writexl::write_xlsx(processedData(), file)
            }
        }
    )
}

data_upload_handler <- function(input, output, session) {
    # Create session-specific directories instead of shared directories
    session_temp_dir <- get_session_path(session, "temp/data")
    
    # Ensure the session-specific directory exists
    if (!dir.exists(session_temp_dir)) {
        dir.create(session_temp_dir, recursive = TRUE)
    }

    # Initialize reactive values to store uploaded file paths and names
    uploadedFilePaths <- reactiveValues(
        plate_layout = list(path = "", name = ""),
        fcs_files = list(),
        template_sheet = list(path = "", name = ""),
        primer_index = list(path = "", name = "")
    )
    
    # Handle Folder Upload
    observeEvent(input$folder_input, {
        if (!is.null(input$folder_input)) {
            # Reset or initialize lists for each file type
            fcs_files_info <- list()

            # Iterate over each file in the uploaded folder
            for (i in 1:nrow(input$folder_input)) {
                # ignore any files that begin with "~$" indicating temporary files
                if (grepl("~$", input$folder_input$name[i], fixed = TRUE)) {
                    cat(sprintf("Ignoring temporary file: %s\n", input$folder_input$name[i]))
                    next
                }

                destPath <- file.path(session_temp_dir, input$folder_input$name[i])
                file.copy(input$folder_input$datapath[i], destPath)
                
                # Categorize and store file info based on naming convention or extension
                if (grepl("plate_spreadsheet", input$folder_input$name[i], ignore.case = TRUE)) {
                    uploadedFilePaths$plate_layout <- list(path = destPath, name = input$folder_input$name[i])
                    cat(sprintf("Plate layout uploaded: %s\n", destPath))
                } else if (grepl("\\.fcs$", input$folder_input$name[i], ignore.case = TRUE)) {
                    # Store the FCS file name first
                    fcs_file_name <- file.path(session_temp_dir, input$folder_input$name[i])
                    
                    # Append the modified information with path and name to the fcs_files_info list
                    fcs_files_info <- c(fcs_files_info, fcs_file_name)
                }
                else if (grepl("template_sheet", input$folder_input$name[i], ignore.case = TRUE)) {
                    uploadedFilePaths$template_sheet <- list(path = destPath, name = input$folder_input$name[i])
                    cat(sprintf("Template sheet uploaded: %s\n", destPath))
                } else if (grepl("primer_index", input$folder_input$name[i], ignore.case = TRUE)) {
                    uploadedFilePaths$primer_index <- list(path = destPath, name = input$folder_input$name[i])
                    cat(sprintf("Primer index file uploaded: %s\n", destPath))
                } else {
                    cat(sprintf("Unrecognized file uploaded: %s\n", destPath))
                }
            }
            
            # Update the fcs_files list in uploadedFilePaths after iterating through all files
            uploadedFilePaths$fcs_files <- fcs_files_info
        }
    }, ignoreNULL = TRUE)
    
    return(uploadedFilePaths)
}

raise_error <- function(errorMessage) {
    shinyjs::hide("spinner")
    print(paste(errorMessage))
    shinyalert::shinyalert("Error", errorMessage, type = "error")
}

data_processing_handler <- function(input, output, session, uploadedFilePaths) {
    # Get session-specific temporary directory
    session_temp_dir <- get_session_path(session, "temp/data")
    
    processedData <- reactiveVal(NULL)  # To store the result of processing
    
    # Listen for the 'process' button click
    observeEvent(input$process, {
        cat("Process button clicked, starting data processing...\n")
        
        # Show processing hint
        shinyjs::show("spinner")

        # Track which type of files are missing
        fcs_files_present <- FALSE
        template_sheet_present <- FALSE
        plate_layout_present <- FALSE

        # Check if there are any FCS files uploaded
        if (length(uploadedFilePaths$fcs_files) > 0) {
            fcs_files_present <- TRUE
        }
        # Check if the template sheet was uploaded
        if (uploadedFilePaths$template_sheet$path != "") {
            template_sheet_present <- TRUE
        }
        # Check if the plate layout sheet was uploaded
        if (uploadedFilePaths$plate_layout$path != "") {
            plate_layout_present <- TRUE
        }

        outputFilePath <- tempfile(fileext = ".csv", tmpdir = session_temp_dir)

        if (!fcs_files_present & !template_sheet_present & !plate_layout_present) {
            raise_error("All required files (i.e. FCS, plate_layout, template) are missing!")
            return(processedData)
        } else {
            # Assuming uploadedFilePaths$fcs_files is a list of file paths
            # Join multiple FCS file paths into a single string if necessary
            fcs_files_argument <- paste(uploadedFilePaths$fcs_files, collapse = " ")
            # Construct the command to call the external Python script with the updated file paths
            command <- sprintf("python scripts/fcs_converter.py --plate-layout %s --fcs-files %s --template-sheet %s --primer-index %s --output-file %s",
                               shQuote(uploadedFilePaths$plate_layout$path), 
                               shQuote(fcs_files_argument), 
                               shQuote(uploadedFilePaths$template_sheet$path), 
                               shQuote(uploadedFilePaths$primer_index$path), 
                               shQuote(outputFilePath))
        }
        
        # Execute the command and capture output, alert on error if python script fails
        command <- paste0(command, " 2>&1")
        tryCatch({
            print(paste("Executing command:", command))
            command_output <- system(command, intern = TRUE)
            exit_status <- attr(command_output, "status")
            print(command_output)

            if (!is.null(exit_status) && exit_status != 0) {
                shinyalert::shinyalert(
                    "Error",
                    paste("Python script failed:\n", paste(command_output, collapse = "\n")),
                    type = "error"
                )
                shinyjs::hide("spinner")
                return(NULL)
            }

            if (!file.exists(outputFilePath)) {
                shinyalert::shinyalert(
                    "Error",
                    "The output file was not created. Please check your input files.",
                    type = "error"
                )
                shinyjs::hide("spinner")
                return(NULL)
            }

            # Now, check if the processed data file was successfully created by the command
            processedData(read.csv(outputFilePath, stringsAsFactors = FALSE))
            shinyalert::shinyalert("Success", "Data processing completed successfully!", type = "success")
            },
            error = function(e) {
                shinyalert::shinyalert("R Error", e$message, type = "error")
                shinyjs::hide("spinner")
                return(NULL)
            }
        )
    })
    return(processedData)
}

# Data display handler function
data_display_handler <- function(input, output, session, processedData) {
    output$dataOutput <- renderDT({
        req(processedData())  # Ensure there's data to display
        
        datatable(processedData(), extensions = 'Buttons', options = list(
            pageLength = 20,
            lengthMenu = list(c(20, 50, 100, -1), c('20 rows', '50 rows', '100 rows', 'Show all')),
            autoWidth = TRUE,
            scrollX = TRUE,
            scrollCollapse = TRUE,
            dom = 'Blfrtip',
            buttons = c('copy', 
                        'csv', 
                        'excel', 
                        'colvis'
                        ),
            searchHighlight = TRUE,
            columnDefs = list(
                list(className = 'dt-center', targets = '_all', width = '200px'),
                list(targets = '_all', createdCell = JS(
                    "function(td, cellData, rowData, row, col) {",
                    "$(td).css({'min-width': '200px'});",
                    "}"
                ))
            ),
            initComplete = JS(
                "function(settings, json) {",
                "$(this.api().table().header()).css({'background-color': '#F0F0F0', 'color': '#000000'});",
                "}"
            )
        ), filter = 'top', rownames = FALSE)
        
        
        
    })
}

ui_display_handler <- function(input, output, session, processedData) {
    output$dynamicUI <- renderUI({
        # First, check if processedData is NULL
        if (is.null(processedData())) {
            homepage_info()
        } else {
            # If processedData is not NULL, check if it's a dataframe with rows
            if (is.data.frame(processedData()) && nrow(processedData()) > 0) {
                # Data is available and is a non-empty dataframe, display the DataTable
                tags$div(style = "overflow-y: scroll; width: 100%;",
                         DT::dataTableOutput("dataOutput"))
            } else if(is.list(processedData()) && length(processedData()) > 0) {
                # If processedData is a list and not empty, handle accordingly
                # This part is optional and should be adapted based on your data structure
                # For example, you might want to display a message or handle list data differently
                tags$div("Data is available but not in dataframe format.")
            } else {
                # If processedData is not NULL but also not a non-empty dataframe or list
                homepage_info()
            }
        }
    })
}

folder_upload_progress_bar <- function(input, output, session) {
    # Placeholder for progress bar UI
    output$upload_progress <- renderUI({
        NULL  # Initially, there's no progress bar
    })
    
    observeEvent(input$folder_input, {
        req(input$folder_input)  # Ensure there's an input
        
        # Initialize the progress bar
        withProgress(message = 'Uploading files...', value = 0, {
            for (i in 1:length(input$folder_input$name)) {
                # Simulate file processing
                Sys.sleep(0.1)  # Replace this with actual file processing
                
                # Update the progress bar
                incProgress(1/length(input$folder_input$name), detail = paste("Processing", input$folder_input$name[i]))
            }
        })
        
        # After processing is complete, show a modal dialog to inform the user
        showModal(modalDialog(
            title = "Upload Complete",
            "All files have been processed. You can now proceed to the next step.",
            easyClose = TRUE,
            footer = modalButton("Close")
        ))
    })
}
