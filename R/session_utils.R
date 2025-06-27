library(uuid)

#' Initialize a user session
#' 
#' @param session The Shiny session object
#' @return A unique session ID
initialise_session <- function(session) {
  # Generate a unique session ID
  session_id <- UUIDgenerate()
  
  # Create session directories
  session_temp_dir <- file.path("temp/data", session_id)
  
  dir.create(session_temp_dir, recursive = TRUE, showWarnings = FALSE)
  
  # Store session info
  session$userData$session_id <- session_id
  session$userData$temp_dir <- session_temp_dir
  
  # Set up cleanup when session ends
  session$onSessionEnded(function() {
    cleanup_session(session_id)
  })
  
  return(session_id)
}

#' Clean up session data
#' 
#' @param session_id The session ID to clean up
cleanup_session <- function(session_id) {
  session_temp_dir <- file.path("temp/data", session_id)
  
  if (dir.exists(session_data_dir)) {
    unlink(session_data_dir, recursive = TRUE)
  }
  
  if (dir.exists(session_temp_dir)) {
    unlink(session_temp_dir, recursive = TRUE)
  }
}

#' Get session-specific path
#' 
#' @param session The Shiny session object
#' @param base_dir The base directory ("data" or "temp/data")
#' @param filename Optional filename to append
#' @return The full path including session ID
get_session_path <- function(session, base_dir, filename = NULL) {
  if (is.null(session$userData$session_id)) {
    stop("Session not initialised")
  }
  
  if (base_dir == "temp/data") {
    path <- session$userData$temp_dir
  } else {
    # Handle custom base directories
    path <- file.path(base_dir, session$userData$session_id)
  }
  
  if (!is.null(filename)) {
    path <- file.path(path, filename)
  }
  
  return(path)
}
