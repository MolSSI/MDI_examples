#location of required codes
LAMMPS_LOC=$(cat ../locations/lammps)

#remove old files
./clean.sh

#launch LAMMPS
cd mm
${LAMMPS_LOC} -mdi "-role ENGINE -name MM -method TCP -port 8021 -hostname localhost" -in water.in > input.out &
cd ../

#launch driver
cd ../../MDI_examples/; python md.py -mdi "-role DRIVER -name driver -method TCP -port 8021" &

wait
