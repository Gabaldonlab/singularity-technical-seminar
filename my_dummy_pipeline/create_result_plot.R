library(ggplot2)

# Get command-line arguments (skip first one since it's the script name)
args <- commandArgs(trailingOnly = TRUE)

# Check if the user provided a file
if (length(args) < 2) {
    stop("Usage: Rscript plot_results.R <input_file.tsv>")
}

# Read the input file
input_file <- args[1]
output_file <- args[2]
df <- read.csv(input_file, sep="\t")

# Simple scatter plot: Bitscore vs. % identity
plot <- ggplot(df, aes(x = pident, y = norm_bitscore)) +
    geom_point(color = "blue") +
    labs(title = "BLAST Hits: % Identity vs Normalized Bitscore",
         x = "% Identity",
         y = "Log-Transformed Bitscore") +
    theme_bw()

# Save plot with a dynamic name
# output_file <- sub(".tsv$", "_plot.png", input_file)
ggsave(output_file, plot)

cat("Plot saved to", output_file, "\n")
