#random forest
library(randomForest)
VGH_2008.2017 <- read.csv("~/Desktop/VGH_2008-2017.csv")
VGH_2008.2017$Collision.Date = as.factor(VGH_2008.2017$Collision.Date)
VGH_2008.2017$Collision.Date = strptime(VGH_2008.2017$Collision.Date,format = "%Y-%m-%d")
VGH_2008.2017$Collision.Date= as.Date(VGH_2008.2017$Collision.Date, format = "%Y-%m-%d")
VGH_2008.2017$Collision.Date
VGH_2008.2017$Collision.Date= weekdays(VGH_2008.2017$Collision.Date)
VGH_2008.2017$Collision.Date = as.factor(VGH_2008.2017$Collision.Date)
rf.model = randomForest(VGH_2008.2017$Injury.Type ~ ., data = VGH_2008.2017, ntree = 501)
#~ 16% OOB
#get the probabilities of each predictions
predictions.rf = predict(rf.model, VGH_2008.2017,type = "prob")

#classification trees
library(rpart)
ctl = rpart.control(minsplit = 2, cp = 1e-8, xval = 10000)
classtree = rpart(VGH_2008.2017$Injury.Type~ ., data = VGH_2008.2017, method = "class", control = ctl, parms=list(split='information'))
plot(classtree, margin=0.01)
text(classtree, use.n=TRUE)
min_cp <- classtree$cptable[which.min(classtree$cptable[,"xerror"]),"CP"]
pruned_tree = prune(classtree, cp = min_cp)
plot(pruned_tree, margin=0.45)
text(pruned_tree, use.n=TRUE)
predictions.tree = predict(pruned_tree, newdata = VGH_2008.2017, type = "class")
table(predictions.tree,VGH_2008.2017$Injury.Type)
#16% misclassificaition rate

#bagged classification trees
library(caret)
ctrl <- trainControl(method="repeatedcv", number = 10, repeats = 5)
bagFit <- train(as.factor(VGH_2008.2017$Injury.Type) ~ ., data = VGH_2008.2017, method = "treebag", trControl = ctrl, preProcess = c("center","scale"),tuneLength = 20)
predictbag = predict(bagFit,newdata = VGH_2008.2017)
table(predictbag, VGH_2008.2017$Injury.Type)
#0.04% misclassification rate, better than rf and classification tree


#neural nets
library(nnet)
ctrl <- trainControl(method="repeatedcv", number = 10, repeats = 5)
nnetFit <- train(as.factor(VGH_2008.2017$Injury.Type) ~ ., data = VGH_2008.2017, method = "nnet", trControl = ctrl, preProcess = c("center","scale"),tuneLength = 20)
nnetFit$modelInfo
nnet<- multinom(VGH_2008.2017$Injury.Type ~ ., data=VGH_2008.2017, maxit=5000)
predidctions.nnet <- predict(nnetFit, newdata=VGH_2008.2017)
table(predictions.nnet, VGH_2008.2017$Injury.Type)

#lda
library(MASS)
ctrl <- trainControl(method="repeatedcv", number = 10, repeats = 5)
ldaFit <- train(as.factor(VGH_2008.2017$Injury.Type) ~ ., data = VGH_2008.2017, method = "lda", trControl = ctrl, preProcess = c("center","scale"),tuneLength = 20)
ldaobj = lda(VGH_2008.2017$Injury.Type ~ ., data = VGH_2008.2017)
predlda = predict(ldaobj, newdata =VGH_2008.2017)
table(predlda$class, VGH_2008.2017$Injury.Type)
#16.2% misclassification rate

#output a csv file with the probabilities of inury, given an injury is present
VGH_2008.2017.final = VGH_2008.2017
VGH_2008.2017.final$minor.prob = predict(bagFit,newdata=VGH_2008.2017.final, type = "prob")[,1]
VGH_2008.2017.final$severe.prob = predict(bagFit,newdata=VGH_2008.2017.final, type = "prob")[,2]
write.csv(VGH_2008.2017.final,"~/Desktop/VGH_2008.2017.final")
