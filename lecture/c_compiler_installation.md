c compiler installation procedurs 

windows 10/11

download MSYS2

https://www.msys2.org/?utm_source=chatgpt.com

choose msys2-x86_64  



let C:\msys64 as it is and follow the rest installation steps 

after that run these commands on MSYS2 UCRT64 terminal

command 1

pacman -Syu

command 2

pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gdb mingw-w64-ucrt-x86_64-make

note: click Y when this question arrives

command 3

gcc --version

command 4

gdb --version

command 5

mingw32-make --version

command 6

$ pacman -Q mingw-w64-ucrt-x86_64-make

command 7

$ pacman -Ql mingw-w64-ucrt-x86_64-make | grep -E '\.exe$'

now open powershell terminal and type these commands

command 1 

notepad setup-c-environment.ps1

note: it will open a ps1 using notepad

paste this powershell script

# C Development Environment Setup

$toolPath = "C:\msys64\ucrt64\bin"

# Get the current user PATH

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Check whether the directory already exists in PATH

if (($userPath -split ';') -notcontains $toolPath) {

    if ($userPath) {

        $newPath = "$userPath;$toolPath"

    }

    else {

        $newPath = $toolPath

    }

    # Save the updated PATH

    [Environment]::SetEnvironmentVariable(

        "Path",

        $newPath,

        "User"
    )

    Write-Host "GCC directory added to PATH!" -ForegroundColor Green

}

else {

    Write-Host "GCC directory already exists in PATH!" -ForegroundColor Yellow
}

# Update PATH in the current PowerShell session

if (($env:Path -split ';') -notcontains $toolPath) {

    $env:Path += ";$toolPath"

}

Write-Host "`nChecking development tools..." -ForegroundColor Cyan

gcc --version

gdb --version

mingw32-make --version

save file and close it

command 2

.\setup-c-environment.ps1


