df <- read.table("sim.csv", header=TRUE)

# fix something strangely wrong with my simulation
df$risk_cancer_per_micro_sv <- rnorm(10000, mean=1/12500000, sd=1/1250000000)
df$expected_cancer_fatalities <- df$passenger_enplanements * df$passenger_exposure_per_screening * df$percentage_ait_screening * df$risk_cancer_per_micro_sv * df$percentage_ait_devices_backscatter
df$increase_ait_fatalities <- df$number_new_driving_fatalities + df$expected_cancer_fatalities - (df$expected_vpi_fatalities - df$expected_ait_vpi_fatalities)

par(mar=par("mar")-0.1)

cumHist <- function(indata, filename, ylab="Cumulative Probability", 
                    subtext="(10, 25, 50, 75, 90) percentiles = (%1.1f, %1.1f, %1.1f, %1.1f, %1.1f) fatalities", ...) {
    png(filename=filename, pointsize=9, width=400, height=400)
	h <- hist(indata, breaks=50, plot=FALSE)
	h$counts <- cumsum(h$counts)
	h$counts <- h$counts/max(h$counts)
	h$density <- cumsum(h$density)
	h$intensities <- h$density

	midvalue10 <- quantile(indata, probs=0.1)
	midvalue25 <- quantile(indata, probs=0.25)
	midvalue50 <- quantile(indata, probs=0.5)
	midvalue75 <- quantile(indata, probs=0.75)
	midvalue90 <- quantile(indata, probs=0.9)
	print (midvalue10)
	print (midvalue25)
	print (midvalue50)
	print (midvalue75)
	print (midvalue90)
	# print(midvalue10, midvalue25, midvalue50, midvalue75, midvalue90)
	plot(h, freq=TRUE,
  	     col="navajowhite2", border="turquoise3",
         ylab=ylab, ...)
    box()
    if (!is.na(subtext)) {
    	title(sub=sprintf(subtext,
  	    	              midvalue10, midvalue25, midvalue50, midvalue75, midvalue90))
  	}
  	dev.off()
  	return(h)
}

h <- cumHist(df$expected_vpi_fatalities, filename="expected_vpi_fatalities.png", main="Current Expected Annual Number of VPI Related Fatalities",
             xlab="Number of Fatalities", subtext="(10, 25, 50, 75, 90) percentiles = (%1.1f, %1.1f, %1.1f, %1.1f, %1.1f) fatalities")
             
h <- cumHist(df$expected_ait_vpi_fatalities, filename="expected_ait_vpi_fatalities.png", main="Expected Annual Number of VPI Related Fatalities with AIT",
             xlab="Number of Fatalities", subtext="(10, 25, 50, 75, 90) percentiles = (%1.1f, %1.1f, %1.1f, %1.1f, %1.1f) fatalities")
             
h <- cumHist(df$increase_ait_fatalities, filename="expected_ait_fatality_increase.png", main="Cumulative histogram of fatality INCREASE from AIT scanning",
        xlab="Number of new fatalities", subtext="(10, 25, 50, 75, 90) percentiles = (%1.1f, %1.1f, %1.1f, %1.1f, %1.1f) fatalities")

h <- cumHist(df$expected_cancer_fatalities, filename="expected_cancer_ait_fatalities.png", main="Cumulative histogram of yearly cancer fatalities from AIT scanning",
        xlab="Number of new cancer fatalities", subtext="(10, 25, 50, 75, 90) percentiles = (%1.1f, %1.1f, %1.1f, %1.1f, %1.1f) fatalities")

h <- cumHist(df$number_passengers_driving, filename="expected_passengers_driving.png", main="Cumulative histogram of yearly passengers choosing to drive",
        xlab="Number of passengers chosing to drive", subtext="(10, 25, 50, 75, 90) percentiles = (%1.0f, %1.0f, %1.0f, %1.0f, %1.0f) passengers")

h <- cumHist(df$number_new_driving_fatalities, filename="expected_driving_fatalities.png", main="Cumulative histogram of new driving fatalities",
        xlab="Driving Fatalities", subtext="(10, 25, 50, 75, 90) percentiles = (%1.1f, %1.1f, %1.1f, %1.1f, %1.1f) fatalities")
