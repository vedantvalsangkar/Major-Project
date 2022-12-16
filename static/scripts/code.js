var editor = CodeMirror.fromTextArea(document.getElementById("assignment_program"),
{
    lineNumbers : true,
    mode: "text/x-csrc",
    theme : "default",
    styleActiveLine: true,
    matchBrackets: true,
    autoCloseBrackets: true
});

var themeInput = document.getElementById("assignment_theme");
var modeInput = document.getElementById("assignment_lang");

function changeTheme(){
    
    var theme = themeInput.options[themeInput.selectedIndex].textContent;
    editor.setOption("theme", theme);
}

function changeMode(){
    var mode = modeInput.selectedIndex;
    console.log(mode);

    if(mode == 0)
    {
        editor.setOption("mode","text/x-csrc");
    }
    if(mode == 1)
    {
        editor.setOption("mode","text/x-c++src");
    }
    if(mode == 2)
    {
        editor.setOption("mode","text/x-java");
    }

    if(mode == 3)
    {
        editor.setOption("mode","python");
    }
    
}



// typedef struct
// #include<stdio.h>
// main()
// import flask
// printf();
// print()
// public void 
// int(input())