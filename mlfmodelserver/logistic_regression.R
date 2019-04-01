library(aod)
library(ggplot2)

pred_fn1 = function(inputs) {
    input_vectors = list(unlist(inputs[1], use.names=FALSE),
	unlist(inputs[2], use.names=FALSE),
	unlist(inputs[3], use.names=FALSE),
	unlist(inputs[4], use.names=FALSE),
	unlist(inputs[5], use.names=FALSE),
	unlist(inputs[6], use.names=FALSE))
    df = as.data.frame(t(as.data.frame(input_vectors)))
    rownames(df) <- NULL
    colnames(df)[1] <- 'admit'
    colnames(df)[2] <- 'gre'
    colnames(df)[3] <- 'gpa'
    colnames(df)[4] <- 'rank'
    summary(df)
    sapply(df, sd)
    xtabs(~admit + rank, data = df)
    df$rank <- factor(df$rank)
    mylogit <- glm(admit ~ gre + gpa + rank, data = df, family = "binomial")
    newdata1 <- with(df, data.frame(gre = mean(gre), gpa = mean(gpa), rank = factor(1:4)))
    newdata1$rankP <- predict(mylogit, newdata = newdata1, type = "response")
    return(newdata1)
}