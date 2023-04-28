# https://r-coder.com/save-plot-r/
# https://stackoverflow.com/questions/75177293/how-to-change-the-label-position-when-plotting-venn-diagram-from-eulerr-package

library(eulerr)

fit <- euler(
    c(
        # "CFG" ONLY
        "CFG" = 3,
        # "CFG&COMP" ONLY
        "CFG&COMP" = 3,
        # "CFG&COMP&RSMI" ONLY
        "CFG&COMP&RSMI" = 1,
        # "CFG&LP" ONLY
        "CFG&LP" = 1,
        # "CFG&RSMI" ONLY
        "CFG&RSMI" = 3,
        # "CFG&RSMI&CFGWSPN" ONLY
        "CFG&RSMI&CFGWSPN" = 1,
        # "CFG&CFGWSPN" ONLY
        "CFG&CFGWSPN" = 2
    ),
    shape = "ellipse",
    input = "disjoint",
)

labels <- c(
    # "CFG" ONLY
    "CFG",
    # "COMP"
    "COMP",
    # "RSMI"
    "RSMI",
    # "LP"
    "LP",
    # "CFGWSPN"
    "CFGWSPN"
)

svg("relationships_among_the_syntactic_biases.svg")
# Remove fills, vary border type
plot(fit, labels = labels, lty = 1:3, legend = FALSE)
dev.off()
