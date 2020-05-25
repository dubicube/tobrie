#########################################################################################
#                                     INVENTORY                                         #
#########################################################################################

# Parse the html file describing the inventory
# Return the result as a list
def processInventoryHTML(htmlFile):
    htmlData = open(htmlFile, "r").read()
    inventory = [[(j[:-6] if j[:-6]!="&#xa0;" else "") for j in i.split("<td class=\"org-left\">")[1:5]] for i in htmlData.split("<tr>")][2:]
    inventory = [[i[0],i[1],i[2],i[3][:-8] if i[3][:-8]!="&#xa0;" else ""] for i in inventory]
    return inventory

# Search an item "data" in the inventory
def searchInventory(data, inventory):
    results = []
    for l in inventory:
        ok = True
        for i in data.lower().split(' '):
            if not(i in l[0].lower() or i in l[1].lower() or i in l[2].lower() or i in l[3].lower()):
                ok = False
        if ok:
            results+=[l]
    return results
