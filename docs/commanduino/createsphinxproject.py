import os


def main():
    print("Please enter the details of the Sphinx project you wish to create.\n")
    projectName = input("Project name: ")
    author = input("Author: ")
    version = input("Project version: ")
    outputDir = input("Output directory: ")
    sourceDir = input("Source code directory: ")

    try:
        print("Creating sphinx project...")
        command = "sphinx-apidoc -F -H {0} -A {1} -V {2} -o {3} {4}".format(projectName, author, version, outputDir, sourceDir)
        print(command)
        # os.system(command)
    except Exception as e:
        print("Error when creating project.")


if __name__=='__main__':
    main()
