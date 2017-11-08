#include <iostream>
#include <TRandom.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TRandom3.h>
#include <TString.h>
#include <TAxis.h>

#include <algorithm>
#include <math.h>

Double_t getNewBaselineCurr( TRandom3* random=NULL) { Double_t scale=1.; if(random != NULL) { scale *= random->Gaus(1.,0.05); }   return scale*0.032; }
Double_t getNewHeightStdDev(bool pessimistic=false) { if(pessimistic) {return 0.15;} else {return 0.20 ;} }
Double_t getNewHeightParam1(bool pessimistic=false) { if(pessimistic) {return 5.77223e9;} else {return 1.78376e9;} } 
Double_t getNewHeightParam2(bool pessimistic=false) { if(pessimistic) {return -1.41389;} else {return -1.35666;} } 
Double_t getNewDosePower() {return 0.7;}
Double_t getNewTempPower() {return 0.5;}

//Basic TID shape parametrized with only 3 parameters
//  - a global normalization factor
//  - a parameter controlling the peak position
//  - two other parameters which are control shape, and normalization but are somewhat redundant with the overall normalization

TF1* getNewShape(Double_t heightScale, Double_t peakPos, TRandom3* random=NULL, Double_t param1=3.163, Double_t param2=0.785) {

  TF1 fInc( "expLogInc","exp([0]*([1]-log(x)-[2]/x))", 0.001, 6);
  fInc.SetParameters(param1,param2,peakPos);
  Double_t nominalIncMax = fInc.GetMaximum(); 
  TString shapeString = TString::Format("(1 + exp([0]*([1]-log(x)-[2]/x))*([3]/%f))*%f", nominalIncMax, getNewBaselineCurr(random)) ;
  TF1* fTot = new TF1("expLog", shapeString.Data(), 0.001, 6);
  fTot->SetParameters(param1, param2, peakPos, heightScale);

  return fTot;
}


//Computes the bump height as a function of the doserate (in krad/h) and the temperature (in C degrees)
//Introduces a gaussian-tossed jitter if a TRandom3 object is provided
Double_t getNewBumpHeightScale(Double_t doseRate, Double_t temperature, bool pessimistic=false,TRandom3* random=NULL) {
    float scale = getNewHeightParam1(pessimistic)*pow(doseRate,getNewDosePower()) * exp(getNewHeightParam2(pessimistic)*pow(temperature+273,getNewTempPower()));
    if (random!=NULL)
      scale *= random->Gaus(1.,getNewHeightStdDev(pessimistic));
    scale = fmax(0.001, scale);
    
    return scale;
}


//Returns a single TID bump shape with fixed height (as a function of the doserate in krad/h and temperature in C degrees) and position
//or with some introduced jitter if a TRandom3 object is provided
TF1 * getNewBumpShape(Double_t doseRate=2.5, Double_t temperature=-10., bool pessimistic=false, TRandom3 * random=NULL) {
    //Generate a peak position on a truncated gaussian (reasonable values between 0.1 and 0.3 ?)
    Double_t peakPos = ((random) ? random->Gaus(0.8,0.06) : 0.8);
    if (peakPos<0.1) peakPos=0.1;


    //Generate a TID bump height scale as a function of the dose rate and temperature
    Double_t heightScale = getNewBumpHeightScale(doseRate, temperature, pessimistic, random);
    
    return getNewShape(heightScale, peakPos, random);
}



//Tosses random bump shapes as a function of the dose rate (krad/h) and temperature (C degrees)
void toyTIDbumpShape_Oct2017(Double_t doseRate=2.5, Double_t temperature=-10., bool pessimistic= false, bool doRandom=true) {
  TCanvas* c1 = new TCanvas(); //Output canvas for test purposes

  //Setting the random generator
  TRandom3 * rangen=NULL;
  rangen = new TRandom3;
  rangen->SetSeed(1);

  int maxIt = 5;
  for (unsigned int iT=0; iT< maxIt; iT++) {

    if (iT == (maxIt-1)) doRandom=false;
    TF1 * fTot = getNewBumpShape(doseRate, temperature, pessimistic, (doRandom) ? rangen : NULL);

    
    fTot->SetLineColorAlpha(((int)rangen->Uniform(10))+1, std::min(1.,1./sqrt(maxIt)));
    
    if (!iT){
      double low = getNewBaselineCurr()*0.8;
      double high = (fTot->GetMaximum() - getNewBaselineCurr())*(1+(getNewHeightStdDev(pessimistic)*(0.3*log10(maxIt)+1))) + getNewBaselineCurr();
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

double tid_new_oct(Double_t temperature, Double_t doseRate, Double_t collecteddose,bool pessimistic=false) {
  double res = getNewBumpShape(doseRate,temperature,false)->Eval(collecteddose/1000.); // krad -> mrad
  double norm = getNewBumpShape(doseRate,temperature,false)->Eval(99999); // Normalize shape.
  //std::cout << Form("NEW DoseRate: %2.2f Temperature: %2.2f CollectedDose: %2.2f Result: %2.4f",doseRate,temperature,collecteddose/1000.,res) << std::endl;
  if (collecteddose == 0) return 1.;
  return res/norm;
}
