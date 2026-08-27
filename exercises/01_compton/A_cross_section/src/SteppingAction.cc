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
/// \file electromagnetic/TestEm13/src/SteppingAction.cc
/// \brief Implementation of the SteppingAction class
//
// 
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#include "SteppingAction.hh"
#include "Run.hh"

#include "G4Colour.hh"
#include "G4Polyline.hh"
#include "G4RunManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4VVisManager.hh"
#include "G4VisAttributes.hh"

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
  G4StepPoint* endPoint = aStep->GetPostStepPoint();
  G4String procName = endPoint->GetProcessDefinedStep()->GetProcessName();
  
  Run* run = static_cast<Run*>(
             G4RunManager::GetRunManager()->GetNonConstCurrentRun()); 
  run->CountProcesses(procName);  

  if (ShowComptonKinematicGuides() && procName == "compt" &&
      aStep->GetTrack()->GetParentID() == 0) {
    DrawComptonKinematicGuides(aStep);
  }
           
  // The experiment measures the first interaction and always stops here.
  // Visualization adds scaled direction guides before aborting the event.
  //
  G4RunManager::GetRunManager()->AbortEvent();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
