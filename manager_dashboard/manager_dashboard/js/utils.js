const getFormData = object => Object.keys(object).reduce((formData, key) => {
    formData.append(key, object[key]);
    return formData;
}, new FormData());


function geojsonToFeatureCollection(geojson){
    if (geojson.type != "FeatureCollection"){
        var collection = {
            type: 'FeatureCollection',
            features: [{"type":"feature", "geometry":geojson}]
        };
        return collection;
    }
    return geojson;
}


async function projectAoi(TMId){
    let response = await fetch(`https://tasking-manager-tm4-production-api.hotosm.org/api/v2/projects/${TMId}/queries/aoi/?as_file=false`);
    const answer = await response.json();
    return answer
}


async function ohsome_request(url, data){
    let response = await fetch(url, {
        "method": 'POST',
        "body": data,
    })
    const answer_ohsome = await response.json();
    return answer_ohsome
}


async function countObjectsInFilter(bpolys, filter){
    let url = "https://api.ohsome.org/v1/elements/count"
    let data = {"bpolys": JSON.stringify(geojsonToFeatureCollection(bpolys)), "filter": filter}
    let answer = await ohsome_request(url, getFormData(data))
    if (answer.status != 200){
        answer.Error = answer.message
        return answer;
    }
    let count = answer.result[0].value
    if ((count != null) & (count > 0) & (count < 100000)){
        // valid result
        return answer;
    }
    else {
        if ((count > 100000)){
            answer.Error = `Area of Interest contains more than 100 000 objects. -> ${count}`
        }
        else{
            answer.Error = "Area of Interest does not contain objects from filter."
        }
        return answer
    }
}


async function validateTMIdAndFilter(TMId, filter){
    let answer_aoi = await projectAoi(TMId)
    if (answer_aoi.Error != null){
        return answer_aoi;
    }
    let answer = await countObjectsInFilter(answer_aoi, filter)
    if (answer.Error != null){
        return answer;
    }
    return answer_aoi
}


async function validateTMId(event){
    var infoOutput = $(event).parent().siblings(".inputInfo")[0];

    TMId = $("#inputTaskGeometriesId").val()
    if (isNaN(TMId) | TMId === ""){
        infoOutput.innerHTML = "Input is not a Number"
        return null
    }
    else{
        answer = await projectAoi(TMId)
        if (answer.Error != null){
            infoOutput.innerHTML = "Project ID not found in HOT Tasking Manager"
            return null
        }
        else {
            infoOutput.innerHTML = "Valid TMId"
            return answer
        }
    }
}


async function validateFilter(event){
    let infoOutput = $(event).parent().siblings(".inputInfo")[0];
    infoOutput.innerHTML = "Starting Requests. This could take some time."

    // get filter value and check if its empty
    let filter;
    let filter_val = $("#inputFilter").val();
    filter_val != "other" ? filter = filter_val : filter = $("#inputFilterText").val();
    if (filter === ""){
        infoOutput.innerHTML = "No filter specified, please enter a valid ohsome filter."
        return
    }

    // check if geometry input is file aoi or TM TMId, handle the cases
    let aoi;
    if ($("#geometryInputOption").val() === "id"){
        aoi = await validateTMId($("#valProjectButton")[0])
        if (aoi === null){
            infoOutput.innerHTML = "Invalid HOT Tasking Manager Project Id. Check the section above."
            return
        }
    }
    else {
        aoi = JSON.parse(projectAoiGeometry)
        if(typeof aoi !== 'object' || aoi === null){
            infoOutput.innerHTML = "No or Invalid file provided. Check the section above."
            return
        }
    }

    // check if the filter is valid
    let answer = await countObjectsInFilter(aoi, filter)

    if (answer.Error != null){
            infoOutput.innerHTML = answer.Error
            return null
    }
    else {
        infoOutput.innerHTML = `Valid filter. ${answer.result[0].value} objects found`
        return answer
    }
}