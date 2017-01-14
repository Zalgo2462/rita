package commands

import (
	"fmt"
	"os"
	"sort"
	"strconv"

	"gopkg.in/mgo.v2/bson"

	"github.com/alecthomas/template"
	"github.com/ocmdev/rita/config"
	"github.com/olekukonko/tablewriter"
	"github.com/urfave/cli"
)

type blresult struct {
	Host    string `bson:"host"`
	Score   int    `bson:"count"`
	Sources string
}

var globalSourcesFlag bool

type blresults []blresult

func (slice blresults) Len() int {
	return len(slice)
}

func (slice blresults) Less(i, j int) bool {
	return slice[j].Score < slice[i].Score
}

func (slice blresults) Swap(i, j int) {
	slice[i], slice[j] = slice[j], slice[i]
}

func init() {
	command := cli.Command{
		Name:  "show-blacklisted",
		Usage: "Print blacklisted information to standard out",
		Flags: []cli.Flag{
			databaseFlag,
			humanFlag,
			cli.BoolFlag{
				Name:        "sources, s",
				Usage:       "Show sources with results",
				Destination: &globalSourcesFlag,
			},
		},
		Action: showBlacklisted,
	}

	bootstrapCommands(command)
}

func showBlacklisted(c *cli.Context) error {
	if c.String("database") == "" {
		return cli.NewExitError("Specify a database with -d", -1)
	}
	conf := config.InitConfig("")
	conf.System.DB = c.String("database")

	var allres blresults

	coll := conf.Session.DB(c.String("database")).C(conf.System.BlacklistedConfig.BlacklistTable)
	coll.Find(nil).All(&allres)

	if globalSourcesFlag {
		for _, res := range allres {
			res.Sources = ""
			cons := conf.Session.DB(c.String("database")).C(conf.System.StructureConfig.ConnTable)
			siter := cons.Find(bson.M{"id_resp_h": res.Host}).Iter()

			var srcStruct struct {
				Src string `bson:"id_origin_h"`
			}

			for siter.Next(&srcStruct) {
				res.Sources += srcStruct.Src + " "
			}
		}
	}

	sort.Sort(allres)

	if humanreadable {
		return showBlacklistedHuman(allres)
	}

	return showBlacklistedCsv(allres)
}

// TODO: Convert this over to tablewriter
// showBlacklisted prints all blacklisted for a given database
func showBlacklistedHuman(allres blresults) error {
	table := tablewriter.NewWriter(os.Stdout)
	headers := []string{"Blacklisted Host", "Connections"}
	if globalSourcesFlag {
		headers = append(headers, "Sources")
	}
	table.SetHeader(headers)
	i := func(i int) string {
		return strconv.Itoa(i)
	}
	for _, res := range allres {
		data := []string{res.Host, i(res.Score)}
		if globalSourcesFlag {
			data = append(data, res.Sources)
		}
		table.Append(data)
	}
	table.Render()
	return nil
}

func showBlacklistedCsv(allres blresults) error {
	tmpl := "{{.Host}}," + `{{.Score}}`
	if globalSourcesFlag {
		tmpl += ", {{.Sources}}"
	}
	tmpl += "\n"
	out, err := template.New("bl").Parse(tmpl)
	if err != nil {
		panic(err)
	}
	var e error = nil
	for _, res := range allres {
		err := out.Execute(os.Stdout, res)
		if err != nil {
			fmt.Fprintf(os.Stdout, "ERROR: Template failure: %s\n", err.Error())
			e = err
		}
	}
	return e
}
