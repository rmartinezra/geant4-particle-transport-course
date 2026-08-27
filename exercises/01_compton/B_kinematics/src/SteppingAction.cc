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
/// \file SteppingAction.cc
/// \brief Implementation of the SteppingAction class
//
// 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#include "SteppingAction.hh"
#include "Run.hh"
#include "HistoManager.hh"
#include "G4RunManager.hh"
#include "G4Event.hh"
#include "G4Colour.hh"
#include "G4Polyline.hh"
#include "G4SystemOfUnits.hh"
#include "G4VVisManager.hh"
#include "G4VisAttributes.hh"

#include <algorithm>
#include <cmath>
#include <cstdlib>

namespace {

G4bool ShowComptonKinematicGuides()
{
  const char* value = std::getenv("G4COURSE_VISUALIZE_COMPTON_GUIDES");
  return value != nullptr && G4String(value) == "1";
}

void DrawComptonKinematicGuides(const G4Step* step)
{
  G4VVisManager* visManager = G4VVisManager::GetConcreteInstance();
  if (visManager == nullptr) return;

  const G4ThreeVector vertex = step->GetPostStepPoint()->GetPosition();
  const G4ThreeVector gammaDirection =
      step->GetPostStepPoint()->GetMomentumDirection().unit();
  G4Polyline gammaGuide;
  gammaGuide.push_back(vertex);
  gammaGuide.push_back(vertex + 1.5*cm*gammaDirection);
  G4VisAttributes gammaStyle(G4Colour(1., 1., 0.));
  gammaStyle.SetLineWidth(4.);
  gammaGuide.SetVisAttributes(gammaStyle);
  visManager->Draw(gammaGuide);

  for (const auto* secondary : *step->GetSecondaryInCurrentStep()) {
    if (secondary->GetDefinition()->GetParticleName() != "e-") continue;
    G4Polyline electronGuide;
    electronGuide.push_back(vertex);
    electronGuide.push_back(
        vertex + 1.0*cm*secondary->GetMomentumDirection().unit());
    G4VisAttributes electronStyle(G4Colour(1., 0., 0.));
    electronStyle.SetLineWidth(4.);
    electronGuide.SetVisAttributes(electronStyle);
    visManager->Draw(electronGuide);
    break;
  }
}

}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SteppingAction::UserSteppingAction(const G4Step* aStep)
{
  const G4StepPoint* endPoint = aStep->GetPostStepPoint();
  G4String procName = endPoint->GetProcessDefinedStep()->GetProcessName();
  
  Run* run = static_cast<Run*>(
             G4RunManager::GetRunManager()->GetNonConstCurrentRun());
  
  G4bool transmit = (endPoint->GetStepStatus() <= fGeomBoundary);  
  if (transmit) { run->CountProcesses(procName); }
  else {                         
    //count real processes and sum track length
    G4double stepLength = aStep->GetStepLength();
    run->CountProcesses(procName);  
    run->SumTrack(stepLength);
  }
  
  //plot final state
  //
  G4AnalysisManager* analysisManager = G4AnalysisManager::Instance();

  // Store a row only for the first Compton interaction of the primary gamma.
  // The angle is relative to the incoming direction, not a fixed lab axis.
  const G4Track* track = aStep->GetTrack();
  if (procName == "compt" && track->GetParentID() == 0 &&
      track->GetDefinition()->GetParticleName() == "gamma") {
    const G4StepPoint* startPoint = aStep->GetPreStepPoint();
    G4ThreeVector initialDirection = startPoint->GetMomentumDirection().unit();
    G4ThreeVector finalDirection = endPoint->GetMomentumDirection().unit();
    G4double cosTheta = initialDirection.dot(finalDirection);
    cosTheta = std::max(-1.0, std::min(1.0, cosTheta));

    G4double electronEnergy = 0.;
    G4double otherSecondaryEnergy = 0.;
    const auto* eventSecondaries = aStep->GetSecondaryInCurrentStep();
    for (const auto* secondary : *eventSecondaries) {
      if (secondary->GetDefinition()->GetParticleName() == "e-") {
        electronEnergy += secondary->GetKineticEnergy();
      }
      else {
        otherSecondaryEnergy += secondary->GetKineticEnergy();
      }
    }

    const G4Event* event = G4RunManager::GetRunManager()->GetCurrentEvent();
    analysisManager->FillNtupleIColumn(0, event->GetEventID());
    analysisManager->FillNtupleDColumn(1, startPoint->GetKineticEnergy()/keV);
    analysisManager->FillNtupleDColumn(2, endPoint->GetKineticEnergy()/keV);
    analysisManager->FillNtupleDColumn(3, cosTheta);
    analysisManager->FillNtupleDColumn(4, std::acos(cosTheta)/deg);
    analysisManager->FillNtupleDColumn(5, electronEnergy/keV);
    analysisManager->FillNtupleSColumn(6, procName);
    analysisManager->FillNtupleDColumn(7, initialDirection.x());
    analysisManager->FillNtupleDColumn(8, initialDirection.y());
    analysisManager->FillNtupleDColumn(9, initialDirection.z());
    analysisManager->FillNtupleDColumn(10, finalDirection.x());
    analysisManager->FillNtupleDColumn(11, finalDirection.y());
    analysisManager->FillNtupleDColumn(12, finalDirection.z());
    analysisManager->FillNtupleDColumn(13, aStep->GetTotalEnergyDeposit()/keV);
    analysisManager->FillNtupleDColumn(14, otherSecondaryEnergy/keV);
    analysisManager->AddNtupleRow();

    if (ShowComptonKinematicGuides()) {
      DrawComptonKinematicGuides(aStep);
    }
  }
     
  //scattered primary particle
  //
  G4int id = 1;
  if (aStep->GetTrack()->GetTrackStatus() == fAlive) {
    G4double energy = endPoint->GetKineticEnergy();      
    analysisManager->FillH1(id,energy);

    id = 2;
    G4ThreeVector direction = endPoint->GetMomentumDirection();
    G4double costeta = direction.x();
    analysisManager->FillH1(id,costeta);     
  }  
  
  //secondaries
  //
  const std::vector<const G4Track*>* secondary 
                                    = aStep->GetSecondaryInCurrentStep();    
  for (size_t lp=0; lp<(*secondary).size(); lp++) {
    G4double charge = (*secondary)[lp]->GetDefinition()->GetPDGCharge();
    if (charge != 0.) { id = 3; } else { id = 5; }
    G4double energy = (*secondary)[lp]->GetKineticEnergy();
    analysisManager->FillH1(id,energy);

    ++id;
    G4ThreeVector direction = (*secondary)[lp]->GetMomentumDirection();      
    G4double costeta = direction.x();
    analysisManager->FillH1(id,costeta);
      
    //energy tranferred to charged secondaries
    if (charge != 0.) { run->SumeTransf(energy); }         
  }
         
  // The experiment stores only the first interaction and always stops here.
  // Visualization adds scaled direction guides before aborting the event.
  //
  G4RunManager::GetRunManager()->AbortEvent();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
