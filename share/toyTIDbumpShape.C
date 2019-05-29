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
Double_t getHeightParam1(bool pessimistic=false) { if(pessimistic) {return 7.82;} else {return 6.133;} } //7.823e
Double_t getHeightParam2(bool pessimistic=false) { if(pessimistic) {return 0.02736; } else { return 0.02143;} }//0.02143; }
//Basic TID shape parametrized with only 3 parameters
//  - a global normalization factor
//  - a parameter controlling the speed of the tail decrease
//  - a parameter controlling the peak position
TF1 * getShape(Double_t heightScale, Double_t tailSpeed, Double_t peakPos, TRandom3* random=NULL) {
  //Initializes the function describing the tail with the tossed values for the parameters
  TF1 fTail("crrcTail","((x-[1])/[0])*exp(-(x-[1])/[0])",0,6);
  fTail.SetParameters(tailSpeed,peakPos);
  Double_t bumpMax = fTail.GetMaximum();
  Double_t posBumpMax = fTail.GetMaximumX();

  //Defines a function describing the bump increase accordingly (i.e. adjusted to fit the bump max)
  TF1 fInc("crrcInc","((x-[1])/[0])*exp(-(x-[1])/[0])",0,6);
  Double_t incSpeed=0.6; //Speed of the TID bump increase, not adjustable (first try)
  Double_t startIrr=0.2; //TID threshold where the bump increase starts, not adjustable (first try)
  fInc.SetParameters(incSpeed,startIrr);
  Double_t maxAtBumpMax = fInc.Eval(posBumpMax);
  fInc.SetParameters(incSpeed,peakPos);

  //Defines the sum of the two function
  TString formTot = TString::Format("([3]*((x-%f)/([4]*%f))*exp(-(x-%f)/[4])*(x>%f)*(x<%f) + [0]*((x-[2])/([1]*%f))*exp(-(x-[2])/[1])*(x>%f)+1)*%f",startIrr,bumpMax,startIrr,startIrr,posBumpMax,bumpMax,posBumpMax, getBaselineCurr(random));
  TF1 * fTot = new TF1("crrcTot",formTot.Data(),0,3.5);
  fTot->SetParameters(heightScale,tailSpeed,peakPos,heightScale*bumpMax/maxAtBumpMax,incSpeed);

  return fTot;
}




//Computes the bump height as a function of the doserate (in krad/h) and the temperature (in C degrees)
//Introduces a 10% gaussian-tossed jitter if a TRandom3 object is provided
Double_t getBumpHeightScale(Double_t doseRate, Double_t temperature, bool pessimistic=false,TRandom3* random=NULL) {
    float scale = getHeightParam1(pessimistic)*doseRate -getHeightParam2(pessimistic)*doseRate*(temperature+273);
    //float incFact = 1 + getHeightParam1()*doseRate -getHeightParam2()*doseRate*(temperature+273);
    //float scale = incFact-1;//0.14*(incFact-1)/0.0515; //adjusting to match the shape height corresponding to 2.5 krad/h and -10C (i.e. incFact=1.98 giving a bump height of 0.0594A)
    /* scale=0.140   --> 0.0815=0.030+0.0515
       incFact=1.98  --> 0.03*1.98=0.0594=0.030+0.0294=0.030+(0.03*1.98-0.03)
       ==> scale=(0.03*1.98-0.03)/0.0515=0.08 --> 0.030+0.0294=0.0594 */
    //incFact=1.47 --> 0.030+
    if (random!=NULL)
      scale *= random->Gaus(1.,getHeightStdDev(pessimistic));
    scale = fmax(0.001, scale);
    
    return scale;
}


//Returns a single TID bump shape with fixed height (as a function of the doserate in krad/h and temperature in C degrees) and position
//or with some introduced jitter if a TRandom3 object is provided
TF1 * getBumpShape(Double_t doseRate=2.5, Double_t temperature=-10., bool pessimistic=false, TRandom3 * random=NULL) {
    //Generate a peak position on a truncated gaussian (reasonable values between 0.1 and 0.3 ?)
    Double_t peakPos = ((random) ? random->Gaus(0.2,0.05) : 0.2);
    //Double_t peakPos = 0.2; //reasonable values between 0.1 and 0.3 ?
    if (peakPos<0.1) peakPos=0.1;

    //Generate a tail decrease speed (reasonable values between 0.4 and 0.6)
    Double_t tailSpeed = ((random) ? random->Gaus(0.47,0.035) : 0.47);
    //Double_t tailSpeed = 0.47; //reasonable values between 0.4 and 0.6

    //Generate a TID bump height scale as a function of the dose rate and temperature
    Double_t heightScale = getBumpHeightScale(doseRate, temperature, pessimistic, random);
    
    return getShape(heightScale, tailSpeed, peakPos, random);
}



//Tosses random bump shapes as a function of the dose rate (krad/h) and temperature (C degrees)
void toyTIDbumpShape(Double_t doseRate=2.5, Double_t temperature=-10., bool pessimistic= false, bool doRandom=true) {
  TCanvas c1; //Output canvas for test purposes

  //Setting the random generator
  TRandom3 * rangen=NULL;
  rangen = new TRandom3;
  rangen->SetSeed(1);

  int maxIt = 1000;
  for (unsigned int iT=0; iT< maxIt; iT++) {

    if (iT == (maxIt-1)) doRandom=false;
    TF1 * fTot = getBumpShape(doseRate, temperature, pessimistic, (doRandom) ? rangen : NULL);

    
//     fTot->SetLineColorAlpha(((int)rangen->Uniform(10))+1, std::min(1.,1./sqrt(maxIt)));
    
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
  
  c1.SaveAs("/tmp/Test.pdf");
}

double tid_new(Double_t temperature, Double_t doseRate, Double_t collecteddose,bool pessimistic) {
  double res = getBumpShape(doseRate,temperature,pessimistic)->Eval(collecteddose/1000.); // krad -> mrad
  double norm = getBumpShape(doseRate,temperature,pessimistic)->Eval(99999); // Normalize shape.
  //std::cout << Form("OLD DoseRate: %2.2f Temperature: %2.2f CollectedDose: %2.2f Result: %2.4f",doseRate,temperature,collecteddose/1000.,res) << std::endl;
  return res/norm;
}
