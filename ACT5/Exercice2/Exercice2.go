package main

import (
	"flag"
	"fmt"
)

// filtrer est une fonction de goroutine qui filtre les nombres premiers en utilisant le crible de Hoare
func filtrer(number int, inChan chan int, resChan chan int, closeSignal chan bool) {
	nextFilter := -1 // prochain filtre à créer
	chanConnectNext := make(chan int) // canal pour se connecter au prochain filtre

	for {
		nbReceived, isOpen := <-inChan // recevoir un nombre du canal d'entrée
		if !isOpen {  // si le canal d'entrée est fermé, quitter la boucle
			break
		}

		if nbReceived%number != 0 { // si le nombre reçu n'est pas un multiple du filtre actuel
			if nextFilter == -1 { // si le prochain filtre n'a pas encore été créé
				nextFilter = nbReceived
				go filtrer(nextFilter, chanConnectNext, resChan, closeSignal) // créer une nouvelle goroutine filtrer avec le nouveau filtre
			} else {
				chanConnectNext <- nbReceived // envoyer le nombre au prochain filtre
			}
		}
	}

	// si un filtre suivant a été créé, fermer le canal associé, en fin, signaler que le dernier filtre est terminé
	if nextFilter != -1 {
		close(chanConnectNext)
	} else {
		closeSignal <- true
	}
	// envoyer le filtre actuel au canal de résultat
	resChan <- number
}

func main() {
	nbRange := flag.Int("n", 10, "nombre limite")
	flag.Parse()
	
	// créer les canaux pour les résultats et les filtres
	resChan := make(chan int, *nbRange-1)
	chanFiltrer := make(chan int)
	closeSignal := make(chan bool)

	// lancer la première goroutine filtrer avec le premier filtre (2)
	go filtrer(2, chanFiltrer, resChan, closeSignal)

	// envoyer les nombres de 3 à nbRange au canal chanFiltrer
	for i := 3; i <= *nbRange; i++ {
		chanFiltrer <- i
	}
	close(chanFiltrer)

	// attendre le signal de fin et fermer le canal des résultats
	go func() {
		<-closeSignal
		close(resChan)
	}()

	// afficher les résultats
	fmt.Print("Liste des nombres premiers jusqu'à ", *nbRange, " saisie sur la ligne de commande :\n")
	resPremier := make([]int, 0)
	for res := range resChan {
		resPremier = append(resPremier, res)
	}
	fmt.Println(resPremier)
}

