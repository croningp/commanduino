import os

def main():
    cmd = generateCommandList()

    for i in range(len(cmd)):
        os.system(cmd[i])

def generateCommandList():
    cmd = []
    cmd.append('cd ../../')
    cmd.append('git checkout gh-pages')
    cmd.append('rm -rf *.html *.js *.inv')
    cmd.append('rm -rf _sources/ _static/ _modules/ docs/')
    cmd.append('git checkout develop')
    cmd.append('cd docs/commanduino/')
    cmd.append('make clean && make html')
    cmd.append('mv -fv _build/html/* ../../')
    cmd.append('cd ../../')
    cmd.append('git add -A')
    cmd.append('git stash')
    cmd.append('git checkout gh-pages')
    cmd.append('git stash pop')
    cmd.append('git add -A')
    cmd.append('git commit -m "Updated the GH pages"')
    cmd.append('git push origin gh-pages')
    cmd.append('git checkout develop')

    return cmd

if __name__ == '__main__':
    main()
