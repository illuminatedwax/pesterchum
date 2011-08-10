#!/bin/bash
# Lex's gif->png script

for file in *.gif
do
    convert ${file} ${file:0:$((${#file}-3))}"png"
done

for file in `ls | grep -G -e "-[1-9]\+.png"`
do
    rm $file
done

for file in `ls | grep -e "-0.png"`
do
    newfile=`echo $file | sed -e 's|\(.*\)-0.png|\1.png|'`
    mv $file $newfile
done

# for file in *.gif
# do
#     rm ${file:0:$((${#file}-3))}"png"
# done
