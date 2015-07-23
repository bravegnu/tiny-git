#!/bin/bash

tdir=$(mktemp -d)

mkdir -p ${tdir}/repo
pushd ${tdir}/repo > /dev/null

tig init
echo "Hello World" > file.txt
sha1sum_1=$(tig commit "Initial content.")
echo "Goodbye World" >> file.txt
sha1sum_2=$(tig commit "Added goodbye world.")
tig checkout -b mybranch ${sha1sum_1}

echo "Branched World" >> file.txt
sha1sum_3=$(tig commit "Added branched world.")

tig checkout master

tig log > ${tdir}/log.txt
cat > ${tdir}/expected.txt <<EOF
${sha1sum_2:0:6} Added goodbye world.
${sha1sum_1:0:6} Initial content.
EOF

if diff -u ${tdir}/log.txt ${tdir}/expected.txt; then
    echo "$0: PASSED"
else
    echo "$0: FAILED"
fi

popd > /dev/null

rm -fr ${tdir}
