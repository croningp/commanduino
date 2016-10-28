import os
import time

def main():
    cmd = generateCommandList()

    for i in range(len(cmd)):
        if i is 0:
            os.chdir('../../')
            time.sleep(1)
            print os.getcwd()
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
            print ("Executing command: \"{0}\"").format(cmd[i])
            time.sleep(2)
            os.system(cmd[i])

def generateCommandList():
    cmd = []
    #cmd.append('cd ../../') 0
    cmd.append('git checkout gh-pages') #0
    cmd.append('rm -rf *.html *.js *.inv') #1
    cmd.append('rm -rf _sources/ _static/ _modules/ docs/') #2
    cmd.append('git checkout develop') #3
    #cmd.append('cd docs/commanduino/') 4
    cmd.append('make clean && make html') #4
    cmd.append('mv -fv _build/html/* ../../') #5
    #cmd.append('cd ../../') 6
    cmd.append('git add -A') #6
    cmd.append('git stash') #7
    cmd.append('git checkout gh-pages') #8
    cmd.append('git stash pop') #9
    cmd.append('rm -rf docs/commanduino/_build/* commanduino/* docs/*')
    cmd.append('git add -A') #10
    cmd.append('git commit -m "Updated the GH pages"') #11
    cmd.append('git push origin gh-pages') #12
    cmd.append('git checkout develop') #13

    return cmd

if __name__ == '__main__':
    main()
