#!/bin/bash

tdir=$(mktemp -d)

mkdir -p ${tdir}/repo
pushd ${tdir}/repo > /dev/null

tig init
echo "Hello World" > file.txt
sha1sum_1=$(tig commit "Initial content.")
echo "Goodbye World" >> file.txt
sha1sum_2=$(tig commit "Added goodbye world.")
tig checkout -b mybranch ${sha1sum_2}

tig checkout master
echo "More text" >> file.txt
sha1sum_3=$(tig commit "Added more text.")

echo "Even More text" >> file.txt
sha1sum_4=$(tig commit "Added even more text.")

tig merge mybranch > ${tdir}/output.txt

cat > ${tdir}/expected.txt <<EOF
tig: up-to-date
EOF

if diff ${tdir}/output.txt ${tdir}/expected.txt; then
    echo "$0: PASSED"
else
    echo "$0: FAILED"
fi

popd > /dev/null

rm -fr ${tdir}
