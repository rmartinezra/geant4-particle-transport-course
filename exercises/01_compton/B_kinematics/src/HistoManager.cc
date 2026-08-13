//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
// 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo...... 

#include "HistoManager.hh"
#include "G4UnitsTable.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

HistoManager::HistoManager()
{
  Book();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void HistoManager::Book()
{
  // Create or get analysis manager
  // The choice of analysis technology is done via selection of a namespace
  // in HistoManager.hh
  G4AnalysisManager* analysisManager = G4AnalysisManager::Instance();
  analysisManager->SetDefaultFileType("csv");
  analysisManager->SetFileName(fFileName);
  analysisManager->SetVerboseLevel(1);
  analysisManager->SetActivation(true);   //enable inactivation of histograms
  
  // Define histograms start values
  const G4int kMaxHisto = 7;
  const G4String id[] = { "0", "1", "2", "3" , "4", "5", "6"};
  const G4String title[] = 
                { "dummy",                                              //0
                  "scattered primary particle: energy spectrum",        //1
                  "scattered primary particle: costheta distribution",  //2
                  "charged secondaries: energy spectrum",               //3
                  "charged secondaries: costheta distribution",         //4
                  "neutral secondaries: energy spectrum",               //5
                  "neutral secondaries: costheta distribution"          //6
                 };  

  // Default values (to be reset via /analysis/h1/set command)               
  G4int nbins = 100;
  G4double vmin = 0.;
  G4double vmax = 100.;

  // Create all histograms as inactivated 
  // as we have not yet set nbins, vmin, vmax
  for (G4int k=0; k<kMaxHisto; k++) {
    G4int ih = analysisManager->CreateH1(id[k], title[k], nbins, vmin, vmax);
    analysisManager->SetH1Activation(ih, false);
  }

  // Event-wise correlation absent from the original TestEm14 histograms.
  analysisManager->CreateNtuple("compton", "First Compton interaction");
  analysisManager->CreateNtupleIColumn("event_id");
  analysisManager->CreateNtupleDColumn("E0_keV");
  analysisManager->CreateNtupleDColumn("Egamma_scattered_keV");
  analysisManager->CreateNtupleDColumn("cos_theta");
  analysisManager->CreateNtupleDColumn("theta_deg");
  analysisManager->CreateNtupleDColumn("electron_kinetic_energy_keV");
  analysisManager->CreateNtupleSColumn("process_name");
  analysisManager->CreateNtupleDColumn("ux_initial");
  analysisManager->CreateNtupleDColumn("uy_initial");
  analysisManager->CreateNtupleDColumn("uz_initial");
  analysisManager->CreateNtupleDColumn("ux_final");
  analysisManager->CreateNtupleDColumn("uy_final");
  analysisManager->CreateNtupleDColumn("uz_final");
  analysisManager->CreateNtupleDColumn("local_energy_deposit_keV");
  analysisManager->CreateNtupleDColumn("other_secondary_energy_keV");
  analysisManager->FinishNtuple();
  analysisManager->SetNtupleFileName(0, "compton_events.csv");
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
