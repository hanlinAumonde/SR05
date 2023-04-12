package main

import (
    "fmt"
    "flag"
    "math/rand"
    "time"
    "runtime"
)

// cutArray découpe un tableau en NB_slices sous-tableaux de tailles approximativement égales,
//puis enregistrer les indexes de chaque portion dans 'result'
func cutArray(arr []int, NB_slices int) [][]int {
	length := len(arr)
	size_slice := length / NB_slices
	remainder := length % NB_slices
	
	result := make([][]int,NB_slices)
	startPoint := 0
	
	for i:=0;i<NB_slices;i++{
		endPoint := startPoint + size_slice
		if remainder > 0{
			endPoint++
			remainder--
		}
		result[i] = []int{startPoint,endPoint}
		startPoint = endPoint
	}
	return result
}

// sommer calcule la somme des éléments d'un sous-tableau et l'envoie sur un canal
func sommer(arr []int,c chan<- int,idProcesseur int){
	somme := 0
    	for i:=0;i<len(arr);i++{
    		somme += arr[i]
    	}
    	fmt.Print("Somme calculé par le processeur ", idProcesseur, ", somme : ", somme, "\n")
    	c <- somme
}

func main(){

	NB_size := flag.Int("n",10,"longeur du tab")	
	flag.Parse()
	
	tabNBs := make([]int,*NB_size+1)
	rand.Seed(time.Now().UnixNano())
	
	// Générer un tableau de nombres aléatoires
	for i:=0; i<*NB_size; i++{
		tabNBs[i] = rand.Intn(100)
	}
	
	fmt.Print("Tableau généré : ", tabNBs, "\n")
	
	// Obtenir le nombre de coeurs de processeur
	var NB_CPU = runtime.NumCPU()
	// Découper le tableau en sous-tableaux selon le nombre de coeurs de processeur
	cutIndex := cutArray(tabNBs,NB_CPU)
	
	// Créer un canal pour recevoir les résultats de somme
	Chan := make(chan int, NB_CPU) 
	// Lancer les goroutines pour calculer la somme de chaque sous-tableau
	for i:=0;i<NB_CPU;i++{
		go sommer(tabNBs[cutIndex[i][0]:cutIndex[i][1]], Chan,i)
	}
	
	// Récupérer les résultats des goroutines et les additionner
	resultat := 0
	for i:=0;i<NB_CPU;i++{
		sommePart := <-Chan
		fmt.Print("Recu : somme calculé : ", sommePart,"\n")
		resultat += sommePart
	}
	
	fmt.Print("Calcul termine, le resultat est : \n",resultat,"\n")
}
