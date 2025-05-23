@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=_build
set DOCSDIR=doc
set GALLERY_EXAMPLES=%SOURCEDIR%\examples\gallery-examples
set AUTOAPI_OUTDIR=%SOURCEDIR%\examples\api\

if "%1" == "" goto help
if "%1" == "pdf" goto pdf
if "%1" == "clean" goto clean
if "%1" == "serve" goto serve

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:pdf
%SPHINXBUILD% -M latex %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
cd "%BUILDDIR%\latex"
for %%f in (*.tex) do (
pdflatex "%%f" --interaction=nonstopmode)

:clean
if exist %BUILDDIR% rmdir /S /Q %BUILDDIR%
if exist %GALLERY_EXAMPLES% rmdir /S /Q %GALLERY_EXAMPLES%
if exist %AUTOAPI_OUTDIR% rmdir /S /Q %AUTOAPI_OUTDIR%


:serve
cd ../
stb serve $(DOCSDIR)/$(SOURCEDIR)


:end
popd
