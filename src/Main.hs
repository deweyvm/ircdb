{-# LANGUAGE DoAndIfThenElse #-}

import System.Environment
import Control.Applicative
import IRCDB.DB.Driver
import IRCDB.Watcher

main :: IO ()
main = do
    args <- getArgs
    if elem "-w" args
    then do let file = args !! 0
            let repop = elem "-rp" args
            watch file repop
    else do let driver = args !! 0
            let chanName = args !! 1
            let actions = if elem "-p" args then [Repopulate, Generate] else [Generate]
            sequence_ $ doAction driver chanName <$> actions
