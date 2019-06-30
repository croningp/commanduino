import os
import time


def main():
    cmd = generateCommandList()

    for i in range(len(cmd)):
        if i is 0:
            os.chdir('../../')
            time.sleep(1)
            print(os.getcwd())
            os.system(cmd[i])
        elif i is 4:
            os.chdir('docs/commanduino')
            time.sleep(1)
            os.system(cmd[i])
        elif i is 6:
            os.chdir('../../')
            time.sleep(1)
            os.system(cmd[i])
        else:
            print("Executing command: \"{0}\"").format(cmd[i])
            time.sleep(2)
            os.system(cmd[i])


def generateCommandList():
    cmd = ['git checkout gh-pages',
           'rm -rf *.html *.js *.inv',
           'rm -rf _sources/ _static/ _modules/ docs/',
           'git checkout develop',
           'make clean && make html',
           'mv -fv _build/html/* ../../',
           'git add -A',
           'git stash',
           'git checkout gh-pages',
           'git stash pop',
           'rm -rf docs/commanduino/_build/* commanduino/* docs/*',
           'git add -A',
           'git commit -m "Updated the GH pages"',
           'git push origin gh-pages',
           'git checkout develop']

    return cmd


if __name__ == '__main__':
    main()
