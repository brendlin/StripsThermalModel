#include <iostream>
#include <TRandom.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TRandom3.h>
#include <TString.h>
#include <TAxis.h>

#include <algorithm>
#include <math.h>

Double_t getBaselineCurr( TRandom3* random=NULL) { Double_t scale=1.; if(random != NULL) { scale *= random->Gaus(1.,0.05); }   return scale*0.032; }
Double_t getHeightStdDev(bool pessimistic=false) { if(pessimistic) {return 0.15;} else {return 0.20 ;} }
Double_t getHeightParam1(bool pessimistic=false) { if(pessimistic) {return 5.77223e9;} else {return 1.78376e9;} } 
Double_t getHeightParam2(bool pessimistic=false) { if(pessimistic) {return -1.41389;} else {return -1.35666;} } 
Double_t getDosePower() {return 0.7;}
Double_t getTempPower() {return 0.5;}

//Basic TID shape parametrized with only 3 parameters
//  - a global normalization factor
//  - a parameter controlling the peak position
//  - two other parameters which are control shape, and normalization but are somewhat redundant with the overall normalization

TF1* getNewShape(Double_t heightScale, Double_t peakPos, TRandom3* random=NULL, Double_t param1=3.163, Double_t param2=0.785) {

  TF1 fInc( "expLogInc","exp([0]*([1]-log(x)-[2]/x))", 0.001, 6);
  fInc.SetParameters(param1,param2,peakPos);
  Double_t nominalIncMax = fInc.GetMaximum(); 
  TString shapeString = TString::Format("(1 + exp([0]*([1]-log(x)-[2]/x))*([3]/%f))*%f", nominalIncMax, getBaselineCurr(random)) ;
  TF1* fTot = new TF1("expLog", shapeString.Data(), 0.001, 6);
  fTot->SetParameters(param1, param2, peakPos, heightScale);

  return fTot;
}


//Computes the bump height as a function of the doserate (in krad/h) and the temperature (in C degrees)
//Introduces a gaussian-tossed jitter if a TRandom3 object is provided
Double_t getBumpHeightScale(Double_t doseRate, Double_t temperature, bool pessimistic=false,TRandom3* random=NULL) {
    float scale = getHeightParam1(pessimistic)*pow(doseRate,getDosePower()) * exp(getHeightParam2(pessimistic)*pow(temperature+273,getTempPower()));
    if (random!=NULL)
      scale *= random->Gaus(1.,getHeightStdDev(pessimistic));
    scale = fmax(0.001, scale);
    
    return scale;
}


//Returns a single TID bump shape with fixed height (as a function of the doserate in krad/h and temperature in C degrees) and position
//or with some introduced jitter if a TRandom3 object is provided
TF1 * getBumpShape(Double_t doseRate=2.5, Double_t temperature=-10., bool pessimistic=false, TRandom3 * random=NULL) {
    //Generate a peak position on a truncated gaussian (reasonable values between 0.1 and 0.3 ?)
    Double_t peakPos = ((random) ? random->Gaus(0.8,0.06) : 0.8);
    if (peakPos<0.1) peakPos=0.1;


    //Generate a TID bump height scale as a function of the dose rate and temperature
    Double_t heightScale = getBumpHeightScale(doseRate, temperature, pessimistic, random);
    
    return getNewShape(heightScale, peakPos, random);
}



//Tosses random bump shapes as a function of the dose rate (krad/h) and temperature (C degrees)
void toyTIDbumpShape(Double_t doseRate=2.5, Double_t temperature=-10., bool pessimistic= false, bool doRandom=true) {
  TCanvas* c1 = new TCanvas(); //Output canvas for test purposes

  //Setting the random generator
  TRandom3 * rangen=NULL;
  rangen = new TRandom3;
  rangen->SetSeed(1);

  int maxIt = 5;
  for (unsigned int iT=0; iT< maxIt; iT++) {

    if (iT == (maxIt-1)) doRandom=false;
    TF1 * fTot = getBumpShape(doseRate, temperature, pessimistic, (doRandom) ? rangen : NULL);

    
    fTot->SetLineColorAlpha(((int)rangen->Uniform(10))+1, std::min(1.,1./sqrt(maxIt)));
    
    if (!iT){
      double low = getBaselineCurr()*0.8;
      double high = (fTot->GetMaximum() - getBaselineCurr())*(1+(getHeightStdDev(pessimistic)*(0.3*log10(maxIt)+1))) + getBaselineCurr();
      fTot->GetYaxis()->SetRangeUser(low, high);
      fTot->Draw();
      fTot->GetYaxis()->SetRangeUser(0.,0.1);
    } else if(iT == (maxIt-1)){
      fTot->SetLineColorAlpha(4,1);
      fTot->SetLineWidth(1);
      fTot->Draw("same");
    } else {
      fTot->Draw("same");
    }
  
  }
  
  const char* caseString = pessimistic ? "pessimistic" : "nominal";
  TString fileString = TString::Format("BumpToys_%.1fkradh_%.fC_%s.pdf", doseRate, temperature, caseString) ;
  c1->SaveAs(fileString);
}
