this is open source project about civil engineering

everyone from any location in the world is welcome to contribute

before you start this install vim here are the procedures

vim installation steps:

windows 10/11

on terminal powershell type these commands in the order you see

command 1

winget install --id vim.vim --exact --source winget

note: this allows you to install vim without microsoft policies

command 2

winget install --id vim.vim --exact --source winget

command 2

winget install --id vim.vim --exact --source winget

note: Find the executable using Windows Search

Instead of searching the entire disk, check these likely locations:

command 3

Get-ChildItem "$env:ProgramFiles\Vim*" -ErrorAction SilentlyContinue

command 4

Get-ChildItem "$env:LOCALAPPDATA\Programs\Vim*" -ErrorAction SilentlyContinue

command 5

Get-ChildItem "$env:LOCALAPPDATA\Programs\Vim" -Recurse -Filter vim.exe

command 6 

& "$env:LOCALAPPDATA\Programs\Vim\vim.exe" --version

command 7 

notepad install-vim-path.ps1

note:paste this powershell script in the notepad file you just opened 

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

$vimPath = "$env:LOCALAPPDATA\Programs\Vim"

if (($userPath -split ';') -notcontains $vimPath) {

    [Environment]::SetEnvironmentVariable(

        "Path",
 
        "$userPath;$vimPath",
        
        "User"
    )
    
    Write-Host "Vim successfully added to PATH!" -ForegroundColor Green

}

else {

    Write-Host "Vim is already in PATH." -ForegroundColor Yellow

}

save file and quit

command 8

.\install-vim-path.ps1

command 9

$env:Path += ";$env:LOCALAPPDATA\Programs\Vim"

command 10

vim --version

note: if anything of these commands failed please contact me in telegram or join tiktok live broadcast and explain the issue 

to contact me:

X account: https://x.com/HassaneZak76591
