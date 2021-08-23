import sys
import time
import typing
import warnings
import zipfile
from pathlib import Path, PurePath

import jpype
from JAbs import SelectedJVMInitializer
from pantarei import chosenProgressReporter


def _extractClassesFromAJar(jarPath: Path) -> typing.Iterator[typing.Tuple[str, ...]]:
	classExt = ".class"
	with zipfile.ZipFile(jarPath) as z:
		for f in z.infolist():
			if f.filename.endswith(classExt):
				path = PurePath(f.filename)
				yield path.parts[:-1] + (path.stem,)


def extractClassesFromAJar(jarPath: Path) -> typing.Any:
	return tuple(sorted(_extractClassesFromAJar(jarPath)))


#scalaPath = Path("/usr/share/scala-2.11/lib")
#scalaPath = Path("./scala-2.13.3/lib")
scalaPath = Path("/usr/share/kaitai-struct-compiler/lib")


additionalClasspath = [Path("/usr/share/maven-repo/org/apache/ant/ant/debian/ant-debian.jar"), Path("./scala-2.13.3/lib/scala-reflect.jar")]
classpath = sorted(scalaPath.glob("*.jar"))
ji = SelectedJVMInitializer(classpath + additionalClasspath, [])

try:
	from scalaTransformArray import decode as decodeScalaSignaturePython

	def decodeScalaSignature(s: bytes) -> bytes:
		s = bytearray(bytes(s))
		l = decodeScalaSignaturePython(s)
		return bytes(s[:l])


except ImportError:
	ByteCodecs = ji.loadClass("scala.reflect.internal.pickling.ByteCodecs")

	def decodeScalaSignature(s: bytes) -> bytes:
		l = ByteCodecs.decode(s)
		s = bytes(s)
		return s[:l]


def getScalaSigAnnotation(classRefl) -> typing.Any:
	for annot in classRefl.annotations:
		if annot.annotationType().name == "scala.reflect.ScalaSignature":
			return annot


def extractAndDecodeScalaSignature(cls) -> bytes:
	classRefl = ji.reflectClass(cls)
	scalaSignAnnot = getScalaSigAnnotation(classRefl)
	if scalaSignAnnot:
		s = scalaSignAnnot.bytes().getBytes("UTF-8")
		return decodeScalaSignature(s)


sc = "scala."
scc = sc + "collection."
scrf = sc + "reflect."
scrfi = scrf + "internal."
sct = sc + "tools."
sctn = sct + "nsc."
sctnbj = sctn + "backend.jvm."
sctnc = sctn + "typechecker."
sctnt = sctn + "transform."
sctntp = sctnt + "patmat."
sctni = sctn + "interpreter."
scrfit = scrfi + "tpe."

sc = "scala."
scc = sc + "collection."
scrf = sc + "reflect."
scrfi = scrf + "internal."
scrfo = scrf + "io."
sct = sc + "tools."
sctn = sct + "nsc."
sctnbj = sctn + "backend.jvm."
sctnc = sctn + "typechecker."
sctnt = sctn + "transform."
sctntp = sctnt + "patmat."
sctni = sctn + "interpreter."
scrfit = scrfi + "tpe."
scrfm = scrf + "macros."
scrfmc = scrfm + "contexts."

blackList = {
	scc + "Iterator$Leading$1",
	scc + "Iterator$PartitionIterator$1",
	scc + "Iterator$Partner$1",
	scc + "parallel.mutable.ParHashMapCombiner$table$2$",
	scrfi + "ExistentialsAndSkolems$$anonfun$packSymbols$1",
	scrfi + "ExistentialsAndSkolems$Deskolemizer$1",
	scrfi + "Internals$SymbolTableInternal$changeOwnerAndModuleClassTraverser$2$",
	scrfit + "TypeMaps$InstantiateDependentMap$StabilizedArgTp$",
	scrfit + "TypeMaps$InstantiateDependentMap$StableArgTp$",
	scrfit + "TypeMaps$InstantiateDependentMap$UnstableArgTp$",
	scrfit + "TypeMaps$InstantiateDependentMap$treeTrans$2$",
	scrfit + "TypeMaps$SubstSymMap$mapTreeSymbols$$anonfun$transform$2",
	scrfit + "TypeMaps$SubstSymMap$mapTreeSymbols$$anonfun$transform$1",
	scrfit + "TypeMaps$SubstTypeMap",
	scrfit + "TypeMaps$SubstTypeMap$trans$2$",
	scc + "immutable.ChampBaseIterator",
	scrfo + "FileZipArchive$FileEntry$1",
	scrfo + "JavaToolsPlatformArchive$$anonfun$iterator$2$FileEntry$4",
	scrfo + "ManifestResources$$anonfun$iterator$1$FileEntry$3",
	scrfo + "URLZipArchive$EmptyFileEntry$1",
	scrfo + "URLZipArchive$FileEntry$2",
	scrfm + "compiler.Validators$Validator$SigGenerator$2$",
	scrfm + "compiler.Validators$Validator$SigGenerator$2$SigmaTypeMap$",
	scrfmc + "Internals$$anon$1$HofTransformer",
	scrfmc + "Internals$$anon$1$HofTypingTransformer",
	scrfmc + "Reifiers$utils$2$",
	sctn + "Global$ClassPathOrdering$2$",
	sctnbj + "GenASM$JPlainBuilder$$anonfun$isClosureApply$1$1",
	sctnbj + "GenASM$JPlainBuilder$Interval$3",
	sctnbj + "GenASM$JPlainBuilder$Interval$4$",
	sctnbj + "GenASM$JPlainBuilder$LineNumberEntry$3",
	sctnbj + "GenASM$JPlainBuilder$LineNumberEntry$4$",
	sctnbj + "GenASM$JPlainBuilder$LocVarEntry$3",
	sctnbj + "GenASM$JPlainBuilder$LocVarEntry$4$",
	sctnbj + "GenASM$JPlainBuilder$scoping$2$",
	sctnbj + "opt.CallGraph$CallsiteInfo$3",
	sctnbj + "opt.CallGraph$CallsiteInfo$4$",
	sctnbj + "opt.ClosureOptimizer$closureInitOrdering$2$",
	sctn + "doc.model.IndexModelFactory$$anon$1$result$2$",
	sctn + "doc.model.ModelFactory$EntityImpl$$anonfun$annotations$1$$typecreator1$1",
	sctn + "interactive.REPL$compiler$2$",
	sctni + "IMain$$typecreator2$1",
	sctni + "Imports$ReqAndHandler$3",
	sctni + "Imports$ReqAndHandler$4$",
	sctni + "ReplVals$AppliedTypeFromTags$1",
	sctn + "symtab.BrowsingLoaders$BrowserTraverser$1",
	sctnt + "Constructors$OmittablesHelper$detectUsages$2$",
	sctnt + "Mixin$MixinTransformer$AddInitBitsTransformer$1",
	sctnt + "Mixin$MixinTransformer$AddInitBitsTransformer$1$$anonfun$transformStats$1",
	sctnt + "Mixin$MixinTransformer$TreeSymSubstituterWithCopying$1",
	sctnt + "Mixin$SingleUseTraverser$2$",
	sctnt + "SpecializeTypes$$anon$2$CollectMethodBodies",
	sctnt + "SpecializeTypes$FullTypeMap$1",
	sctntp + "Interface$TypedSubstitution$Substitution$substIdentsForTrees$2$",
	sctntp + "Logic$PropositionalLogic$gatherEqualities$2$",
	sctntp + "Logic$PropositionalLogic$rewriteEqualsToProp$2$",
	sctntp + "MatchAnalysis$MatchAnalyzer$VariableAssignment$3",
	sctntp + "MatchAnalysis$MatchAnalyzer$VariableAssignment$3$$anonfun$uniqueEqualTo$1$$anonfun$apply$20",
	sctntp + "MatchAnalysis$MatchAnalyzer$VariableAssignment$4$",
	sctntp + "MatchApproximation$MatchApproximator$TreeMakersToProps$TreeMakerToProp$condStrategy$2$",
	sctntp + "MatchTranslation$MatchTranslator$ExtractorCallRegular",
	sctntp + "MatchTranslation$MatchTranslator$ExtractorCallRegular$splice$2$",
	sctntp + "ScalaLogic$TreesAndTypesDomain$Var$ExcludedPair$2",
	sctntp + "ScalaLogic$TreesAndTypesDomain$Var$ExcludedPair$3$",
	sctntp + "Solving$Solver$TseitinSolution$3",
	sctntp + "Solving$Solver$TseitinSolution$4$",
	sctntp + "TreeAndTypeAnalysis$CheckableTreeAndTypeAnalysis$typeArgsToWildcardsExceptArray$2$",
	sctnc + "Implicits$ImplicitSearch$ImplicitComputation$LocalShadower$1",
	sctnc + "Implicits$ImplicitSearch$ImplicitComputation$LocalShadower$1",
	sctnc + "Implicits$ImplicitSearch$ImplicitComputation$NoShadower$2$",
	sctnc + "Infer$Inferencer$InferMethodAlternativeTwice$1",
	sctnc + "Infer$Inferencer$InferTwice$1",
	sctnc + "Macros$UnsigmaTypeMap$2$",
	sctnc + "RefChecks$RefCheckTransformer$LevelInfo",
	sctnc + "RefChecks$RefCheckTransformer$MixinOverrideError$3",
	sctnc + "RefChecks$RefCheckTransformer$MixinOverrideError$4$",
	sctnc + "Typers$Typer$ArrayInstantiation$2$",
	sctnc + "Typers$Typer$checkEphemeralDeep$2$",
	sct + "reflect.FormatInterpolator$$typecreator1$1",

	# scala 2.13
	sc + "reflect.macros.compiler.Validators$Validator$SigGenerator$1$",
	sc + "reflect.macros.compiler.Validators$Validator$SigGenerator$1$SigmaTypeMap$",
	sc + "reflect.macros.contexts.Reifiers$utils$1$",
	sc + "tools.nsc.Global$ClassPathOrdering$1$",
	sc + "tools.nsc.InterpreterLoop$$anon$1$Compat$1",
	sc + "tools.nsc.doc.model.IndexModelFactory$$anon$1$result$1$",
	sc + "tools.nsc.doc.model.ModelFactory$EntityImpl$$typecreator1$1",
	sc + "tools.nsc.interactive.REPL$compiler$1$",
	sc + "tools.nsc.interpreter.Imports$ReqAndHandler$1",
	sc + "tools.nsc.interpreter.Imports$ReqAndHandler$2$",
	sc + "tools.nsc.interpreter.shell.Scripted$$typecreator2$1",
	sctnt + "Constructors$OmittablesHelper$DetectAssigns$1",
	sctnt + "Constructors$OmittablesHelper$detectUsages$1$",
	sctnt + "Erasure$ErasureTransformer$$anon$4$SingletonInstanceCheck$",
	sctnt + "Mixin$MixinTransformer$SingleUseTraverser$1$",
	sctnt + "async.AsyncAnalysis$UnsupportedAwaitAnalyzer$traverser$1$",
	sctnt + "async.Lifter$companionship$1$",
	sctnt + "async.Lifter$traverser$1$",
	sctnt + "async.LiveVariables$FindUseTraverser$1",
	sctntp + "Interface$TypedSubstitution$Substitution$substIdentsForTrees$1$",
	sctntp + "Logic$PropositionalLogic$gatherEqualities$1$",
	sctntp + "Logic$PropositionalLogic$rewriteEqualsToProp$1$",
	sctntp + "MatchAnalysis$MatchAnalyzer$VariableAssignment$1$",
	sctntp + "MatchApproximation$MatchApproximator$TreeMakersToProps$TreeMakerToProp$condStrategy$1$",
	sctntp + "MatchTranslation$MatchTranslator$ExtractorCallRegular$splice$1$",
	sctntp + "ScalaLogic$TreesAndTypesDomain$Var$ExcludedPair$1",
	sctntp + "ScalaLogic$TreesAndTypesDomain$Var$ExcludedPair$2$",
	sctntp + "Solving$Solver$TseitinSolution$1",
	sctntp + "Solving$Solver$TseitinSolution$2$",
	sctntp + "TreeAndTypeAnalysis$CheckableTreeAndTypeAnalysis$typeArgsToWildcardsExceptArray$1$",
	sctnc + "Contexts$Context$DictionarySubstituter$1",
	sctnc + "Contexts$Context$ReferenceSubstituter$1",
	sctnc + "Implicits$ImplicitSearch$ImplicitComputation$Candidate$1",
	sctnc + "Implicits$ImplicitSearch$ImplicitComputation$Candidate$2$",
	sctnc + "Infer$Inferencer$typeMap$1$",
	sctnc + "MacroAnnotationNamers$MacroAnnotationNamer$PatchedContext$1",
	sctnc + "MacroAnnotationNamers$MacroAnnotationNamer$PatchedContext$1$$anon$3",
	sctnc + "MacroAnnotationNamers$MacroAnnotationNamer$PatchedContext$1$PatchedLookupResult",
	sctnc + "RefChecks$RefCheckTransformer$MixinOverrideError$1",
	sctnc + "RefChecks$RefCheckTransformer$MixinOverrideError$2$",
	sctnc + "Typers$Typer$checkEphemeralDeep$1$",
	sctnc + "Typers$Typer$setRange$1$",
	sctnc + "Typers$Typer$substResetForOriginal$1$",
	scc + "immutable.HashMap$accum$1",
	sc + "util.hashing.MurmurHash3$accum$1",
	sc + "volatile",
	scrfi + "Positions$worker$1$",
	scrfi + "Positions$worker$1$solidChildrenCollector$",
	scrfi + "tpe.TypeMaps$InstantiateDependentMap$treeTrans$1$",
	scrfi + "tpe.TypeMaps$SubstTypeMap$trans$1$",
	sc + "reflect.io.ManifestResources$FileEntry$2",
	sc + "reflect.io.URLZipArchive$FileEntry$1",
	
	"fastparse.utils.MacroUtils$$typecreator1$1",
	"fastparse.utils.MacroUtils$$typecreator2$1",
	"sourcecode.Args$$typecreator7$1",
	"sourcecode.Args$$typecreator8$1",
	"sourcecode.File$$typecreator5$1",
	"sourcecode.FullName$$typecreator3$1",
	"sourcecode.FullName$Machine$$typecreator4$1",
	"sourcecode.Impls$$typecreator10$1",
	"sourcecode.Impls$$typecreator9$1",
	"sourcecode.Line$$typecreator6$1",
	"sourcecode.Name$$typecreator1$1",
	"sourcecode.Name$Machine$$typecreator2$1",
}


def harvestSignatures() -> None:
	with zipfile.ZipFile("./scalaSignatures.zip", mode="w", compression=zipfile.ZIP_LZMA) as z:
		for jarPath in classpath[:]:
			classesComps = extractClassesFromAJar(jarPath)
			with chosenProgressReporter(len(classesComps), "extracting signatures") as pb:
				for clsComps in classesComps[:]:
					clsName = ".".join(clsComps)
					#print(clsName, file=sys.stderr)
					if clsName in blackList:
						pb.report(key=clsName, incr=1, op="blocked")
						continue
					#for i in range(10):
					#	time.sleep(0.01)
					#	sys.stderr.flush()
					pb.report(key=clsName, incr=0, op="Loading class")
					try:
						cls = ji.loadClass(clsName)
					except BaseException:
						pb.report(key=clsName, incr=1, op="import failure")
						continue

					sigDecoded = extractAndDecodeScalaSignature(cls)
					if sigDecoded:
						with z.open(str(PurePath(jarPath.stem)._make_child(clsComps)), mode="w") as sf:
							sf.write(sigDecoded)
							pb.report(key=clsName, incr=1, op="Extracted")
					else:
						pb.report(key=clsName, incr=1, op="empty")
						pass


if __name__ == "__main__":
	harvestSignatures()
