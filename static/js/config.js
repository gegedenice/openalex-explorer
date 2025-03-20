/*-----------------------Marseille source--------------------------*/
var summaries = [
    {
        "name": "Is OA",
        "panel": "middle",
        "value": "open_access_is_oa"
    },
    {
        "name": "OA status",
        "panel": "middle",
        "value": "open_access_oa_status"
    },
    {
        "name": "Publication date",
        "panel": "bottom",
        //"value": "publication_date",
        "value":  function () {
            if(this["publication_date"]){
             return new Date(Date.parse(this["publication_date"]))
            }
        }
    },
    {
        "name": "Publisher",
        "panel": "left",
        "value": "primary_location_host_organization_name"
    },
    {
        "name": "Authors",
        "panel": "left",
        //"value": "authorships_author_display_name",
        "value":  function () {
            if(this["authorships_author_display_name"]){
             return this["authorships_author_display_name"].split("|")
            }
        }
    },
    {
        "name": "Institutions",
        "panel": "left",
        //"value": "authorships_institutions_display_name",
        "value":  function () {
            if(this["authorships_institutions_display_name"]){
              return this["authorships_institutions_display_name"].split("|")
            }
        }
        
    },
    {
        "name": "Topics",
        "panel": "left",
        "value":  function () {
            if(this["topics_display_name"]){
              return this["topics_display_name"].split("|")
            }
        }
        
    },
    {
        "name": "Language",
        "panel": "left",
        "value": "language",
        "collapsed": true 
    },
    {
        "name": "Publication type",
        "panel": "left",
        "value": "type"
    },
   /* {
        "name": "Journal",
        "panel": "left",
        "value": "primary_location_display_name"
    },
    {
        "name": "Publication year",
        "panel": "left",
        "value": function () {
            return this["publication_year"].toString();
        }
    },*/
    {
        "name": "APC amount",
        "panel": "right",
        "value": "apc_paid"
    },
    {
        "name": "Cites",
        "panel": "right",
        "value": "referenced_works_count",
        "collapsed": true 
    },
    {
        "name": "Cited by",
        "panel": "right",
        "value": "cited_by_count",
        "collapsed": true
    },
    {
        "name": "Distinct countries count",
        "panel": "right",
        "value": "countries_distinct_count",
        "collapsed": true
    },
    {
        "name": "Distinct institutions count",
        "panel": "right",
        "value": "institutions_distinct_count",
        "collapsed": true
    },
    {
        "name": "Locations count",
        "panel": "right",
        "value": "locations_count",
        "collapsed": true
    },
   /* {
        "name": "FWCI",
        "panel": "right",
        "value": "fwci"
    },*/
    {
        "name": "Is in Top 1 percent",
        "panel": "right",
        "value": "percentiles_is_in_top_1_percent",
        "collapsed": true
    },
    {
        "name": "Is in Top 10 percent",
        "panel": "right",
        "value": "percentiles_is_in_top_10_percent",
        "collapsed": true
    },
    {
        name: "Record Text",
        value: function (_rec) {
          var str = "";
          // location
          str +=
            '<div class="iteminfo iteminfo_1"><b>Title:</b> ' +
            this["title"] +
            "</div>";
          str +=
            '<div class="iteminfo iteminfo_1"><b>Ids:</b>' +
            " <u>DOI</u>:" +
            this["doi"] +
            " - <u>OpenALex ID</u>:" +
            this["id"] +
            " - <u>Pubmed ID:" +
            this["pmid"] +
            " - <u>Microsoft ID" +
            this["mag"] +
            "</div>";
  
          /*str += '<span class="item_details">'; 
          str += '<div class="iteminfo iteminfo_1"><b>Bibliographic: </b>';
          str += " <u>Publication type</u>:" + this["type"];
          str += " <u>Publication year</u>:" + this["publication_year"];
          str += " <u>Publisher</u>:" + this["primary_location_display_name"];
          str += " <u>Authors</u>:" + this["authorships_author_display_name"];
          str += " <u>Affiliations</u>:" + this["authorships_institutions_display_name"];
          str += " <u>Topics</u>:" + this["topics_display_name"];
          str += "</div>";

          str +=  '<div class="iteminfo iteminfo_2"><b>Open Access:</b>';
          str += " <u>IS OA</u>:" + this["open_access_is_oa"];
          str += " <u>OA status</u>:" + this["open_access_oa_status"];
            "</div>";
  
          str += "</span>";*/
  
          return str;
        },
      },
]

var recordDisplay = {
    viewAs: "list",
    textBy: "Record Text",
    //sortBy: "publication_date",
    list_sortColWidth: 45,
    list_sortVizWidth: 0,
    list_sortInverse: true,
    scatterXBy: "referenced_works_count",
    scatterYBy: "cited_by_count",
    colorBy: "open_access_is_oa",
    sizeBy: "institutions_distinct_count",
    timeSeriesBy: "referenced_works_count",
  }
