package main

import (
	kingpin "gopkg.in/alecthomas/kingpin.v2"
	"fmt"
)

var (
	   a = kingpin.Flag("account", "Account").Short('a').Required().String()
	auth = kingpin.Flag("auth", "Authentication File").Short('s').Default("bank.auth").String()
	  ip = kingpin.Flag("ip", "IP Address").Short('i').Default("127.0.0.1").String()
	port = kingpin.Flag("port", "Port").Short('p').Default("3000").Int()
	card = kingpin.Flag("card", "Card File").Short('c').Default(".card").String()

)

func main() {
	kingpin.Parse()
	fmt.Printf("%v\n", *a)
}

